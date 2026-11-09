"""Módulo de transformação da camada Raw para Refined.

Realiza a extração filtrada, validação de tipos, junção de nomes de clubes e
cálculo de métricas de partida (pontos, saldo e resultado).
"""

import csv
from pathlib import Path
from typing import Dict, List, Optional

try:
    from src.config import (
        COMPETITION_ID,
        EDICAO_ESPORTIVA,
        RAW_CLUBS_FILE,
        RAW_GAMES_FILE,
        REFINED_GAMES_FILE,
        TEMPORADA_ORIGEM,
    )
except ImportError:
    # Permite execução direta quando o diretório raiz não está no PYTHONPATH
    import sys

    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from src.config import (
        COMPETITION_ID,
        EDICAO_ESPORTIVA,
        RAW_CLUBS_FILE,
        RAW_GAMES_FILE,
        REFINED_GAMES_FILE,
        TEMPORADA_ORIGEM,
    )


def load_clubs_map(clubs_csv_path: Path) -> Dict[int, str]:
    """Carrega o mapeamento de club_id para nome oficial do clube a partir de clubs.csv."""
    clubs_map: Dict[int, str] = {}
    with open(clubs_csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid_str = row.get("club_id", "").strip()
            if cid_str and cid_str.isdigit():
                clubs_map[int(cid_str)] = row.get("name", "").strip()
    return clubs_map


def calculate_match_metrics(home_goals: int, away_goals: int) -> dict:
    """Calcula o resultado da partida, pontos e saldo de gols."""
    if home_goals > away_goals:
        resultado = "VITORIA_MANDANTE"
        pontos_m = 3
        pontos_v = 0
    elif home_goals < away_goals:
        resultado = "VITORIA_VISITANTE"
        pontos_m = 0
        pontos_v = 3
    else:
        resultado = "EMPATE"
        pontos_m = 1
        pontos_v = 1

    return {
        "resultado_partida": resultado,
        "pontos_mandante": pontos_m,
        "pontos_visitante": pontos_v,
        "saldo_gols_mandante": home_goals - away_goals,
        "saldo_gols_visitante": away_goals - home_goals,
    }


def transform_single_match(
    raw_row: dict,
    clubs_map: Dict[int, str],
    target_competition: str = COMPETITION_ID,
    target_season: str = TEMPORADA_ORIGEM,
    sporting_edition: int = EDICAO_ESPORTIVA,
) -> Optional[dict]:
    """Valida, filtra e transforma um registro individual de partida da camada raw.

    Retorna None caso o registro não pertença ao recorte desejado.
    """
    comp_id = raw_row.get("competition_id", "").strip()
    season = raw_row.get("season", "").strip()

    if comp_id != target_competition or season != target_season:
        return None

    game_id = int(raw_row["game_id"])
    home_id = int(raw_row["home_club_id"])
    away_id = int(raw_row["away_club_id"])
    home_goals = int(raw_row["home_club_goals"])
    away_goals = int(raw_row["away_club_goals"])

    # Nome limpo obtido de clubs.csv (com fallback para nome em games.csv se necessário)
    home_name = clubs_map.get(home_id, raw_row.get("home_club_name", "").strip())
    away_name = clubs_map.get(away_id, raw_row.get("away_club_name", "").strip())

    metrics = calculate_match_metrics(home_goals, away_goals)

    return {
        "game_id": game_id,
        "temporada_origem": season,
        "edicao_esportiva": sporting_edition,
        "competition_id": comp_id,
        "data_partida": raw_row.get("date", "").strip(),
        "rodada": raw_row.get("round", "").strip(),
        "id_mandante": home_id,
        "nome_mandante": home_name,
        "id_visitante": away_id,
        "nome_visitante": away_name,
        "gols_mandante": home_goals,
        "gols_visitante": away_goals,
        **metrics,
    }


def run_transform_refined(
    games_csv_path: Path = RAW_GAMES_FILE,
    clubs_csv_path: Path = RAW_CLUBS_FILE,
    output_csv_path: Path = REFINED_GAMES_FILE,
) -> Path:
    """Executa a transformação completa de raw para refined e grava o CSV de saída."""
    clubs_map = load_clubs_map(clubs_csv_path)

    transformed_records: List[dict] = []
    with open(games_csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            transformed = transform_single_match(row, clubs_map)
            if transformed is not None:
                transformed_records.append(transformed)

    # Ordena as partidas cronologicamente e por game_id para reprodutibilidade
    transformed_records.sort(key=lambda r: (r["data_partida"], r["game_id"]))

    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "game_id",
        "temporada_origem",
        "edicao_esportiva",
        "competition_id",
        "data_partida",
        "rodada",
        "id_mandante",
        "nome_mandante",
        "id_visitante",
        "nome_visitante",
        "gols_mandante",
        "gols_visitante",
        "resultado_partida",
        "pontos_mandante",
        "pontos_visitante",
        "saldo_gols_mandante",
        "saldo_gols_visitante",
    ]

    with open(output_csv_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(transformed_records)

    print(
        f"Transformação concluída: {len(transformed_records)} partidas salvas em {output_csv_path}"
    )
    return output_csv_path


if __name__ == "__main__":
    run_transform_refined()
