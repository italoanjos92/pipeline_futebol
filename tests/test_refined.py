"""Testes automatizados da camada Refined e de lógica de transformação.

Compatível nativamente com unittest e com pytest (pytest>=8.0.0).
"""

import csv
import unittest
from collections import Counter
from datetime import datetime
from pathlib import Path

from src.config import (
    RAW_CLUBS_FILE,
    RAW_COMPETITIONS_FILE,
    REFINED_GAMES_FILE,
)
from src.transform_refined import (
    calculate_match_metrics,
    load_clubs_map,
    transform_single_match,
)


class TestRegrasDeNegocioSinteticas(unittest.TestCase):
    """Testes com casos sintéticos (em memória) para validação isolada das regras."""

    def test_formula_pontos_vitoria_mandante(self):
        """Mandante vence (3 x 1): 3 pontos mandante, 0 pontos visitante, saldo correto."""
        m = calculate_match_metrics(home_goals=3, away_goals=1)
        self.assertEqual(m["resultado_partida"], "VITORIA_MANDANTE")
        self.assertEqual(m["pontos_mandante"], 3)
        self.assertEqual(m["pontos_visitante"], 0)
        self.assertEqual(m["saldo_gols_mandante"], 2)
        self.assertEqual(m["saldo_gols_visitante"], -2)
        self.assertEqual(m["pontos_mandante"] + m["pontos_visitante"], 3)

    def test_formula_pontos_vitoria_visitante(self):
        """Visitante vence (0 x 2): 0 pontos mandante, 3 pontos visitante, saldo correto."""
        m = calculate_match_metrics(home_goals=0, away_goals=2)
        self.assertEqual(m["resultado_partida"], "VITORIA_VISITANTE")
        self.assertEqual(m["pontos_mandante"], 0)
        self.assertEqual(m["pontos_visitante"], 3)
        self.assertEqual(m["saldo_gols_mandante"], -2)
        self.assertEqual(m["saldo_gols_visitante"], 2)
        self.assertEqual(m["pontos_mandante"] + m["pontos_visitante"], 3)

    def test_formula_pontos_empate(self):
        """Empate (2 x 2): 1 ponto para cada, saldo zero, soma de pontos igual a 2."""
        m = calculate_match_metrics(home_goals=2, away_goals=2)
        self.assertEqual(m["resultado_partida"], "EMPATE")
        self.assertEqual(m["pontos_mandante"], 1)
        self.assertEqual(m["pontos_visitante"], 1)
        self.assertEqual(m["saldo_gols_mandante"], 0)
        self.assertEqual(m["saldo_gols_visitante"], 0)
        self.assertEqual(m["pontos_mandante"] + m["pontos_visitante"], 2)

    def test_transform_single_match_caso_sintetico_valido(self):
        """Valida mapeamento completo de uma linha sintética dentro do recorte."""
        raw_row = {
            "game_id": "99999",
            "competition_id": "BRA1",
            "season": "2024",
            "date": "2025-05-10",
            "round": "5. Matchday",
            "home_club_id": "100",
            "away_club_id": "200",
            "home_club_goals": "2",
            "away_club_goals": "1",
            "home_club_name": "Time Casa Raw",
            "away_club_name": "Time Fora Raw",
        }
        clubs_map = {100: "Clube Casa Oficial", 200: "Clube Fora Oficial"}

        resultado = transform_single_match(raw_row, clubs_map)
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["game_id"], 99999)
        self.assertEqual(resultado["temporada_origem"], "2024")
        self.assertEqual(resultado["edicao_esportiva"], 2025)
        self.assertEqual(resultado["competition_id"], "BRA1")
        self.assertEqual(resultado["nome_mandante"], "Clube Casa Oficial")
        self.assertEqual(resultado["nome_visitante"], "Clube Fora Oficial")
        self.assertEqual(resultado["resultado_partida"], "VITORIA_MANDANTE")
        self.assertEqual(resultado["pontos_mandante"], 3)
        self.assertEqual(resultado["pontos_visitante"], 0)

    def test_transform_single_match_filtra_fora_do_recorte(self):
        """Verifica se jogos de outra temporada ou competição são descartados (retornam None)."""
        clubs_map = {100: "Clube A", 200: "Clube B"}

        # Linha de outra temporada
        row_outra_temporada = {
            "game_id": "1",
            "competition_id": "BRA1",
            "season": "2023",
            "home_club_id": "100",
            "away_club_id": "200",
            "home_club_goals": "1",
            "away_club_goals": "0",
        }
        self.assertIsNone(transform_single_match(row_outra_temporada, clubs_map))

        # Linha de outra competição
        row_outra_comp = {
            "game_id": "2",
            "competition_id": "GB1",
            "season": "2024",
            "home_club_id": "100",
            "away_club_id": "200",
            "home_club_goals": "1",
            "away_club_goals": "0",
        }
        self.assertIsNone(transform_single_match(row_outra_comp, clubs_map))


class TestArquivoRefinadoGerado(unittest.TestCase):
    """Testes de integridade e regras de negócio sobre o arquivo gerado em data/refined/."""

    @classmethod
    def setUpClass(cls):
        """Carrega os registros do arquivo gerado e tabelas de apoio se existirem."""
        cls.caminho_arquivo = REFINED_GAMES_FILE
        if not cls.caminho_arquivo.exists():
            raise unittest.SkipTest(
                f"Arquivo {cls.caminho_arquivo} ainda não foi gerado."
            )

        with open(cls.caminho_arquivo, mode="r", encoding="utf-8") as f:
            cls.registros = list(csv.DictReader(f))

        # Apoio: Clubes
        with open(RAW_CLUBS_FILE, mode="r", encoding="utf-8") as f:
            cls.clubes_apoio_ids = {
                int(r["club_id"]) for r in csv.DictReader(f) if r.get("club_id")
            }

        # Apoio: Competições
        with open(RAW_COMPETITIONS_FILE, mode="r", encoding="utf-8") as f:
            cls.competicoes_apoio_ids = {
                r["competition_id"].strip()
                for r in csv.DictReader(f)
                if r.get("competition_id")
            }

    def test_total_registros_e_chaves_unicas(self):
        """Deve conter exatamente 380 partidas e 380 game_id distintos."""
        self.assertEqual(len(self.registros), 380)
        game_ids = [r["game_id"] for r in self.registros]
        self.assertEqual(len(set(game_ids)), 380)

    def test_mapeamento_temporada_e_edicao(self):
        """Todos os registros devem ter temporada_origem='2024' e edicao_esportiva='2025'."""
        for r in self.registros:
            self.assertEqual(r["temporada_origem"], "2024")
            self.assertEqual(r["edicao_esportiva"], "2025")
            self.assertEqual(r["competition_id"], "BRA1")

    def test_datas_validas_e_intervalo(self):
        """Todas as datas devem ser válidas e estar no intervalo delimitado (2025-03-29 a 2025-12-07)."""
        dt_inicio = datetime.strptime("2025-03-29", "%Y-%m-%d")
        dt_fim = datetime.strptime("2025-12-07", "%Y-%m-%d")

        for r in self.registros:
            data_str = r["data_partida"]
            data_dt = datetime.strptime(data_str, "%Y-%m-%d")
            self.assertTrue(
                dt_inicio <= data_dt <= dt_fim,
                f"Data {data_str} fora do intervalo de 2025 no jogo {r['game_id']}",
            )

    def test_gols_inteiros_e_nao_negativos(self):
        """Gols de mandante e visitante devem ser inteiros e não negativos (>= 0)."""
        for r in self.registros:
            gm = int(r["gols_mandante"])
            gv = int(r["gols_visitante"])
            self.assertGreaterEqual(gm, 0)
            self.assertGreaterEqual(gv, 0)

    def test_coerencia_placar_pontos_resultado_e_saldo(self):
        """Valida se pontos, resultado e saldos são 100% coerentes com o placar de cada jogo."""
        for r in self.registros:
            gm = int(r["gols_mandante"])
            gv = int(r["gols_visitante"])
            pm = int(r["pontos_mandante"])
            pv = int(r["pontos_visitante"])
            sm = int(r["saldo_gols_mandante"])
            sv = int(r["saldo_gols_visitante"])
            res = r["resultado_partida"]

            self.assertEqual(sm, gm - gv)
            self.assertEqual(sv, gv - gm)

            if gm > gv:
                self.assertEqual(res, "VITORIA_MANDANTE")
                self.assertEqual(pm, 3)
                self.assertEqual(pv, 0)
                self.assertEqual(pm + pv, 3)
            elif gm < gv:
                self.assertEqual(res, "VITORIA_VISITANTE")
                self.assertEqual(pm, 0)
                self.assertEqual(pv, 3)
                self.assertEqual(pm + pv, 3)
            else:
                self.assertEqual(res, "EMPATE")
                self.assertEqual(pm, 1)
                self.assertEqual(pv, 1)
                self.assertEqual(pm + pv, 2)

    def test_referencias_em_tabelas_de_apoio(self):
        """IDs de clubes e de competição devem existir nas tabelas de apoio clubs.csv e competitions.csv."""
        for r in self.registros:
            self.assertIn(r["competition_id"], self.competicoes_apoio_ids)
            self.assertIn(int(r["id_mandante"]), self.clubes_apoio_ids)
            self.assertIn(int(r["id_visitante"]), self.clubes_apoio_ids)

    def test_reconciliacao_gols(self):
        """A soma dos gols calculados deve bater com os totais apurados no recorte."""
        total_gols_mandante = sum(int(r["gols_mandante"]) for r in self.registros)
        total_gols_visitante = sum(int(r["gols_visitante"]) for r in self.registros)

        self.assertEqual(total_gols_mandante, 580)
        self.assertEqual(total_gols_visitante, 379)
        self.assertEqual(total_gols_mandante + total_gols_visitante, 959)

    def test_equilibrio_por_ids_dos_clubes(self):
        """Cada um dos 20 IDs de clubes deve ter exatamente 19 jogos como mandante e 19 como visitante."""
        mandantes_ids = Counter(int(r["id_mandante"]) for r in self.registros)
        visitantes_ids = Counter(int(r["id_visitante"]) for r in self.registros)

        self.assertEqual(len(mandantes_ids), 20)
        self.assertEqual(len(visitantes_ids), 20)

        for cid in mandantes_ids:
            self.assertEqual(
                mandantes_ids[cid],
                19,
                f"Clube ID {cid} não tem 19 jogos como mandante",
            )
            self.assertEqual(
                visitantes_ids[cid],
                19,
                f"Clube ID {cid} não tem 19 jogos como visitante",
            )

    def test_confronto_em_cada_mando_por_par_de_clubes(self):
        """Para cada par de clubes dos 20 times (190 pares), deve haver exatamente 1 jogo de ida e 1 de volta."""
        clubes_ids = sorted(list({int(r["id_mandante"]) for r in self.registros}))
        self.assertEqual(len(clubes_ids), 20)

        confrontos = Counter(
            (int(r["id_mandante"]), int(r["id_visitante"])) for r in self.registros
        )

        total_pares = 0
        for i in range(len(clubes_ids)):
            for j in range(i + 1, len(clubes_ids)):
                c1 = clubes_ids[i]
                c2 = clubes_ids[j]
                total_pares += 1
                self.assertEqual(
                    confrontos[(c1, c2)],
                    1,
                    f"Falta ou duplica confronto com {c1} mandante e {c2} visitante",
                )
                self.assertEqual(
                    confrontos[(c2, c1)],
                    1,
                    f"Falta ou duplica confronto com {c2} mandante e {c1} visitante",
                )

        self.assertEqual(total_pares, 190)

    def test_ordenacao_cronologica(self):
        """As partidas devem estar ordenadas de forma não-decrescente por data_partida."""
        datas = [r["data_partida"] for r in self.registros]
        self.assertEqual(datas, sorted(datas))


if __name__ == "__main__":
    unittest.main()
