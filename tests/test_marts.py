"""Testes automatizados da camada analítica (Marts).

Compatível nativamente com unittest e com pytest (pytest>=8.0.0).
Valida regras matemáticas, consistência de classificação, agregação de mando e casos sintéticos.
"""

import csv
import sqlite3
import unittest
from pathlib import Path

from src.build_marts import (
    create_in_memory_connection,
    execute_sql_query,
    load_refined_table,
)
from src.config import (
    MART_CLASSIFICACAO_FILE,
    MART_DESEMPENHO_MANDO_FILE,
    MART_RESUMO_GERAL_FILE,
    REFINED_GAMES_FILE,
    SQL_CLASSIFICACAO_FILE,
    SQL_DESEMPENHO_MANDO_FILE,
    SQL_RESUMO_GERAL_FILE,
)


class TestMartsCasosSinteticos(unittest.TestCase):
    """Testes com base de dados sintética em memória para validar as consultas SQL de Marts."""

    def setUp(self):
        self.conn = create_in_memory_connection()
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE refined_partidas (
                game_id INTEGER PRIMARY KEY,
                temporada_origem TEXT,
                edicao_esportiva INTEGER,
                competition_id TEXT,
                data_partida TEXT,
                rodada TEXT,
                id_mandante INTEGER,
                nome_mandante TEXT,
                id_visitante INTEGER,
                nome_visitante TEXT,
                gols_mandante INTEGER,
                gols_visitante INTEGER,
                resultado_partida TEXT,
                pontos_mandante INTEGER,
                pontos_visitante INTEGER,
                saldo_gols_mandante INTEGER,
                saldo_gols_visitante INTEGER
            );
            """
        )
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_classificacao_detecta_empate_residual_sem_desempate_arbitrario(self):
        """Dois clubes com campanha exatamente igual devem receber a mesma posição e flag empate_residual=1."""
        cursor = self.conn.cursor()
        partidas_mock = [
            (1, "2024", 2025, "BRA1", "2025-04-01", "1", 10, "Clube A", 30, "Clube C", 2, 0, "VITORIA_MANDANTE", 3, 0, 2, -2),
            (2, "2024", 2025, "BRA1", "2025-04-02", "1", 20, "Clube B", 30, "Clube C", 2, 0, "VITORIA_MANDANTE", 3, 0, 2, -2),
            (3, "2024", 2025, "BRA1", "2025-04-03", "2", 10, "Clube A", 20, "Clube B", 0, 0, "EMPATE", 1, 1, 0, 0),
        ]
        cursor.executemany(
            "INSERT INTO refined_partidas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            partidas_mock,
        )
        self.conn.commit()

        headers, rows = execute_sql_query(self.conn, SQL_CLASSIFICACAO_FILE)
        tabela = [dict(zip(headers, r)) for r in rows]

        clube_a = next(r for r in tabela if r["club_id"] == 10)
        clube_b = next(r for r in tabela if r["club_id"] == 20)

        # Mesma posição calculada
        self.assertEqual(clube_a["posicao_calculada"], 1)
        self.assertEqual(clube_b["posicao_calculada"], 1)

        # Flag de empate residual ativa
        self.assertEqual(clube_a["empate_residual"], 1)
        self.assertEqual(clube_b["empate_residual"], 1)

        # Sem desempate forçado
        self.assertEqual(clube_a["pontos"], clube_b["pontos"])
        self.assertEqual(clube_a["vitorias"], clube_b["vitorias"])
        self.assertEqual(clube_a["saldo_gols"], clube_b["saldo_gols"])
        self.assertEqual(clube_a["gols_pro"], clube_b["gols_pro"])


class TestArquivoMartsGerados(unittest.TestCase):
    """Testes sobre os arquivos gerados em data/marts/."""

    @classmethod
    def setUpClass(cls):
        """Carrega os marts gerados em data/marts/ se existirem."""
        if not (
            MART_CLASSIFICACAO_FILE.exists()
            and MART_DESEMPENHO_MANDO_FILE.exists()
            and MART_RESUMO_GERAL_FILE.exists()
        ):
            raise unittest.SkipTest(
                "Arquivos da camada data/marts/ ainda não foram gerados."
            )

        with open(MART_CLASSIFICACAO_FILE, mode="r", encoding="utf-8") as f:
            cls.classificacao = list(csv.DictReader(f))

        with open(MART_DESEMPENHO_MANDO_FILE, mode="r", encoding="utf-8") as f:
            cls.desempenho_mando = list(csv.DictReader(f))

        with open(MART_RESUMO_GERAL_FILE, mode="r", encoding="utf-8") as f:
            cls.resumo_geral = list(csv.DictReader(f))

        with open(REFINED_GAMES_FILE, mode="r", encoding="utf-8") as f:
            cls.refined_partidas = list(csv.DictReader(f))

    def test_formula_pontos_classificacao(self):
        """Para cada clube: pontos = 3 * vitórias + empates."""
        for c in self.classificacao:
            pts = int(c["pontos"])
            v = int(c["vitorias"])
            e = int(c["empates"])
            self.assertEqual(
                pts,
                3 * v + e,
                f"Fórmula de pontos inválida para {c['clube']}",
            )

    def test_total_jogos_classificacao(self):
        """Para cada clube: jogos = vitórias + empates + derrotas = 38."""
        for c in self.classificacao:
            j = int(c["jogos"])
            v = int(c["vitorias"])
            e = int(c["empates"])
            d = int(c["derrotas"])
            self.assertEqual(j, 38)
            self.assertEqual(j, v + e + d)

    def test_reconciliacao_gols_pro_e_contra(self):
        """Soma dos gols pró = soma dos gols contra = total de gols na camada refinada (959)."""
        total_gp = sum(int(c["gols_pro"]) for c in self.classificacao)
        total_gc = sum(int(c["gols_contra"]) for c in self.classificacao)
        total_gols_refinados = sum(
            int(r["gols_mandante"]) + int(r["gols_visitante"])
            for r in self.refined_partidas
        )

        self.assertEqual(total_gp, total_gols_refinados)
        self.assertEqual(total_gc, total_gols_refinados)
        self.assertEqual(total_gp, 959)

    def test_soma_dos_saldos_igual_a_zero(self):
        """Invariante matemática: a soma dos saldos de gols de todos os clubes deve ser exatamente 0."""
        soma_saldos = sum(int(c["saldo_gols"]) for c in self.classificacao)
        self.assertEqual(soma_saldos, 0)

    def test_desempenho_mando_soma_igual_ao_total(self):
        """Para cada clube no mart de mando: casa + fora = total de jogos e total de pontos."""
        for d in self.desempenho_mando:
            jm = int(d["jogos_mandante"])
            jv = int(d["jogos_visitante"])
            tj = int(d["total_jogos"])
            pm = int(d["pontos_mandante"])
            pv = int(d["pontos_visitante"])
            tp = int(d["total_pontos"])

            self.assertEqual(jm, 19)
            self.assertEqual(jv, 19)
            self.assertEqual(tj, 38)
            self.assertEqual(jm + jv, tj)
            self.assertEqual(pm + pv, tp)

    def test_cruzamento_mando_e_classificacao_por_clube(self):
        """Cruza por club_id e edicao_esportiva os totais de jogos e pontos entre mando e classificacao."""
        mando_por_chave = {
            (int(d["club_id"]), int(d["edicao_esportiva"])): d
            for d in self.desempenho_mando
        }

        self.assertEqual(len(self.classificacao), 20)
        self.assertEqual(len(mando_por_chave), 20)

        for c in self.classificacao:
            chave = (int(c["club_id"]), int(c["edicao_esportiva"]))
            self.assertIn(chave, mando_por_chave, f"Clube {c['clube']} ausente no mart de mando")

            m = mando_por_chave[chave]

            # Reconciliação estrita entre os dois marts
            self.assertEqual(int(c["jogos"]), int(m["total_jogos"]))
            self.assertEqual(int(c["pontos"]), int(m["total_pontos"]))
            self.assertEqual(
                int(c["vitorias"]),
                int(m["vitorias_mandante"]) + int(m["vitorias_visitante"]),
            )
            self.assertEqual(
                int(c["empates"]),
                int(m["empates_mandante"]) + int(m["empates_visitante"]),
            )
            self.assertEqual(
                int(c["derrotas"]),
                int(m["derrotas_mandante"]) + int(m["derrotas_visitante"]),
            )
            self.assertEqual(
                int(c["gols_pro"]),
                int(m["gols_pro_mandante"]) + int(m["gols_pro_visitante"]),
            )
            self.assertEqual(
                int(c["gols_contra"]),
                int(m["gols_contra_mandante"]) + int(m["gols_contra_visitante"]),
            )
            self.assertEqual(
                int(c["saldo_gols"]),
                int(m["saldo_gols_mandante"]) + int(m["saldo_gols_visitante"]),
            )

    def test_ordenacao_criterios_classificacao(self):
        """Posições calculadas devem ser não-decrescentes e respeitar a ordem dos critérios."""
        posicoes = [int(c["posicao_calculada"]) for c in self.classificacao]
        self.assertEqual(posicoes, sorted(posicoes))

        for i in range(len(self.classificacao) - 1):
            c1 = self.classificacao[i]
            c2 = self.classificacao[i + 1]

            p1, p2 = int(c1["pontos"]), int(c2["pontos"])
            v1, v2 = int(c1["vitorias"]), int(c2["vitorias"])
            s1, s2 = int(c1["saldo_gols"]), int(c2["saldo_gols"])
            g1, g2 = int(c1["gols_pro"]), int(c2["gols_pro"])

            self.assertGreaterEqual((p1, v1, s1, g1), (p2, v2, s2, g2))

    def test_reconciliacao_resumo_geral(self):
        """Recalcula métricas diretamente de partidas refinadas e compara com resumo_geral.csv."""
        self.assertEqual(len(self.resumo_geral), 1)
        resumo = self.resumo_geral[0]

        total_partidas = len(self.refined_partidas)
        self.assertEqual(total_partidas, 380)

        # Cálculo direto sobre a camada refinada
        vm = sum(1 for r in self.refined_partidas if r["resultado_partida"] == "VITORIA_MANDANTE")
        vv = sum(1 for r in self.refined_partidas if r["resultado_partida"] == "VITORIA_VISITANTE")
        emp = sum(1 for r in self.refined_partidas if r["resultado_partida"] == "EMPATE")

        pct_vm = round((vm / total_partidas) * 100.0, 2)
        pct_vv = round((vv / total_partidas) * 100.0, 2)
        pct_emp = round((emp / total_partidas) * 100.0, 2)

        total_gm = sum(int(r["gols_mandante"]) for r in self.refined_partidas)
        total_gv = sum(int(r["gols_visitante"]) for r in self.refined_partidas)
        media_gols = round((total_gm + total_gv) / total_partidas, 2)

        # Comparação estrita com resumo_geral.csv
        self.assertEqual(int(resumo["total_partidas"]), total_partidas)
        self.assertEqual(int(resumo["total_clubes"]), 20)
        self.assertEqual(int(resumo["total_gols"]), total_gm + total_gv)
        self.assertEqual(int(resumo["total_gols_mandante"]), total_gm)
        self.assertEqual(int(resumo["total_gols_visitante"]), total_gv)
        self.assertEqual(float(resumo["media_gols_partida"]), media_gols)

        self.assertEqual(int(resumo["total_vitorias_mandante"]), vm)
        self.assertEqual(int(resumo["total_vitorias_visitante"]), vv)
        self.assertEqual(int(resumo["total_empates"]), emp)

        self.assertEqual(float(resumo["pct_vitorias_mandante"]), pct_vm)
        self.assertEqual(float(resumo["pct_vitorias_visitante"]), pct_vv)
        self.assertEqual(float(resumo["pct_empates"]), pct_emp)

        self.assertEqual(vm + vv + emp, total_partidas)


if __name__ == "__main__":
    unittest.main()
