"""Módulo de configuração central do pipeline de futebol.

Define caminhos de diretórios, identificadores e constantes do recorte analítico.
"""

from pathlib import Path

# Diretórios base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_REFINED_DIR = DATA_DIR / "refined"
DATA_MARTS_DIR = DATA_DIR / "marts"
SQL_DIR = BASE_DIR / "sql"

# Arquivos de entrada brutos (raw)
RAW_GAMES_FILE = DATA_RAW_DIR / "games.csv"
RAW_CLUBS_FILE = DATA_RAW_DIR / "clubs.csv"
RAW_COMPETITIONS_FILE = DATA_RAW_DIR / "competitions.csv"

# Arquivo de saída da camada tratada (refined)
REFINED_GAMES_FILE = DATA_REFINED_DIR / "partidas_brasileirao_2025.csv"

# Arquivos SQL da camada analítica (marts)
SQL_CLASSIFICACAO_FILE = SQL_DIR / "marts_classificacao.sql"
SQL_DESEMPENHO_MANDO_FILE = SQL_DIR / "marts_desempenho_mando.sql"
SQL_RESUMO_GERAL_FILE = SQL_DIR / "marts_resumo_geral.sql"

# Arquivos de saída da camada analítica (marts)
MART_CLASSIFICACAO_FILE = DATA_MARTS_DIR / "classificacao_calculada.csv"
MART_DESEMPENHO_MANDO_FILE = DATA_MARTS_DIR / "desempenho_mando.csv"
MART_RESUMO_GERAL_FILE = DATA_MARTS_DIR / "resumo_geral.csv"

# Definições do recorte de dados
# Na fonte Transfermarkt, a edição esportiva 2025 está rotulada com season = '2024'.
COMPETITION_ID = "BRA1"
TEMPORADA_ORIGEM = "2024"
EDICAO_ESPORTIVA = 2025
NOME_COMPETICAO = "Campeonato Brasileiro Série A"
