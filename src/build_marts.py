"""Módulo de construção da camada analítica (Marts).

Carrega a tabela tratada (refined) em um banco de dados SQLite em memória (:memory:),
executa as consultas SQL analíticas e exporta os resultados consolidados para data/marts/.
"""

import csv
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from src.config import (
        DATA_MARTS_DIR,
        MART_CLASSIFICACAO_FILE,
        MART_DESEMPENHO_MANDO_FILE,
        MART_RESUMO_GERAL_FILE,
        REFINED_GAMES_FILE,
        SQL_CLASSIFICACAO_FILE,
        SQL_DESEMPENHO_MANDO_FILE,
        SQL_RESUMO_GERAL_FILE,
    )
except ImportError:
    import sys

    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from src.config import (
        DATA_MARTS_DIR,
        MART_CLASSIFICACAO_FILE,
        MART_DESEMPENHO_MANDO_FILE,
        MART_RESUMO_GERAL_FILE,
        REFINED_GAMES_FILE,
        SQL_CLASSIFICACAO_FILE,
        SQL_DESEMPENHO_MANDO_FILE,
        SQL_RESUMO_GERAL_FILE,
    )


def create_in_memory_connection() -> sqlite3.Connection:
    """Cria e retorna uma conexão SQLite em memória (:memory:)."""
    return sqlite3.connect(":memory:")


def load_refined_table(
    conn: sqlite3.Connection,
    refined_csv_path: Path = REFINED_GAMES_FILE,
) -> int:
    """Lê o CSV da camada refinada e cria a tabela temporária refined_partidas no SQLite."""
    cursor = conn.cursor()

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

    rows_to_insert: List[tuple] = []
    with open(refined_csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows_to_insert.append(
                (
                    int(row["game_id"]),
                    row["temporada_origem"],
                    int(row["edicao_esportiva"]),
                    row["competition_id"],
                    row["data_partida"],
                    row["rodada"],
                    int(row["id_mandante"]),
                    row["nome_mandante"],
                    int(row["id_visitante"]),
                    row["nome_visitante"],
                    int(row["gols_mandante"]),
                    int(row["gols_visitante"]),
                    row["resultado_partida"],
                    int(row["pontos_mandante"]),
                    int(row["pontos_visitante"]),
                    int(row["saldo_gols_mandante"]),
                    int(row["saldo_gols_visitante"]),
                )
            )

    cursor.executemany(
        """
        INSERT INTO refined_partidas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        rows_to_insert,
    )
    conn.commit()
    return len(rows_to_insert)


def execute_sql_query(
    conn: sqlite3.Connection,
    sql_file_path: Path,
) -> Tuple[List[str], List[Tuple]]:
    """Lê um arquivo SQL, executa no SQLite e retorna os nomes das colunas e os registros."""
    with open(sql_file_path, mode="r", encoding="utf-8") as f:
        sql_content = f.read()

    cursor = conn.cursor()
    cursor.execute(sql_content)
    headers = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    return headers, rows


def export_query_to_csv(
    headers: List[str],
    rows: List[Tuple],
    output_path: Path,
) -> Path:
    """Grava o resultado da consulta em um arquivo CSV na pasta de destino."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    return output_path


def run_build_marts(
    refined_csv_path: Path = REFINED_GAMES_FILE,
    marts_dir: Path = DATA_MARTS_DIR,
) -> Dict[str, Path]:
    """Orquestra a criação de todos os marts analíticos utilizando SQLite em memória."""
    conn = create_in_memory_connection()
    try:
        total_linhas = load_refined_table(conn, refined_csv_path)
        print(f"Refined carregado no SQLite em memória: {total_linhas} partidas.")

        outputs: Dict[str, Path] = {}

        # 1. Classificação Calculada
        h_class, r_class = execute_sql_query(conn, SQL_CLASSIFICACAO_FILE)
        p_class = marts_dir / "classificacao_calculada.csv"
        export_query_to_csv(h_class, r_class, p_class)
        outputs["classificacao"] = p_class
        print(f"Mart gerado: {p_class} ({len(r_class)} clubes)")

        # 2. Desempenho por Mando
        h_mando, r_mando = execute_sql_query(conn, SQL_DESEMPENHO_MANDO_FILE)
        p_mando = marts_dir / "desempenho_mando.csv"
        export_query_to_csv(h_mando, r_mando, p_mando)
        outputs["desempenho_mando"] = p_mando
        print(f"Mart gerado: {p_mando} ({len(r_mando)} clubes)")

        # 3. Resumo Geral de Indicadores
        h_resumo, r_resumo = execute_sql_query(conn, SQL_RESUMO_GERAL_FILE)
        p_resumo = marts_dir / "resumo_geral.csv"
        export_query_to_csv(h_resumo, r_resumo, p_resumo)
        outputs["resumo_geral"] = p_resumo
        print(f"Mart gerado: {p_resumo} ({len(r_resumo)} linha consolidada)")

        return outputs
    finally:
        conn.close()


if __name__ == "__main__":
    run_build_marts()
