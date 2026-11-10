import pandas as pd
import streamlit as st

from src.config import (
    EDICAO_ESPORTIVA,
    NOME_COMPETICAO,
    MART_CLASSIFICACAO_FILE,
    MART_DESEMPENHO_MANDO_FILE,
    MART_RESUMO_GERAL_FILE,
)


st.set_page_config(
    page_title="Dashboard de Futebol",
    layout="wide",
)

st.title(f"{NOME_COMPETICAO} — {EDICAO_ESPORTIVA}")
st.caption(
    "Painel analítico dos dados do pipeline. "
    "A classificação é calculada e não representa uma tabela oficial."
)


def carregar_csv(caminho, colunas_obrigatorias):
    if not caminho.is_file():
        st.error(f"Arquivo não encontrado: {caminho}")
        st.info(
            "Os CSVs precisam ser gerados pelo pipeline antes "
            "de abrir o dashboard."
        )
        st.stop()

    try:
        dados = pd.read_csv(caminho)
    except (OSError, ValueError, UnicodeError) as erro:
        st.error(f"Não foi possível ler {caminho.name}: {erro}")
        st.stop()

    faltantes = set(colunas_obrigatorias) - set(dados.columns)

    if faltantes:
        st.error(
            f"Colunas ausentes em {caminho.name}: "
            + ", ".join(sorted(faltantes))
        )
        st.stop()

    dados = dados.loc[
        pd.to_numeric(dados["edicao_esportiva"], errors="coerce")
        == EDICAO_ESPORTIVA
    ].copy()

    if dados.empty:
        st.warning(
            f"Não há dados da edição {EDICAO_ESPORTIVA} "
            f"em {caminho.name}."
        )
        st.stop()

    return dados


colunas_classificacao = [
    "posicao_calculada",
    "edicao_esportiva",
    "club_id",
    "clube",
    "jogos",
    "vitorias",
    "empates",
    "derrotas",
    "gols_pro",
    "gols_contra",
    "saldo_gols",
    "pontos",
    "aproveitamento_pct",
    "empate_residual",
]

colunas_mando = [
    "edicao_esportiva",
    "club_id",
    "clube",
    "jogos_mandante",
    "jogos_visitante",
    "pontos_mandante",
    "pontos_visitante",
    "aproveitamento_mandante_pct",
    "aproveitamento_visitante_pct",
]

colunas_resumo = [
    "edicao_esportiva",
    "competition_id",
    "total_partidas",
    "total_clubes",
    "total_gols",
    "media_gols_partida",
    "total_vitorias_mandante",
    "total_vitorias_visitante",
    "total_empates",
]

classificacao = carregar_csv(
    MART_CLASSIFICACAO_FILE,
    colunas_classificacao,
)

mando = carregar_csv(
    MART_DESEMPENHO_MANDO_FILE,
    colunas_mando,
)

resumo = carregar_csv(
    MART_RESUMO_GERAL_FILE,
    colunas_resumo,
)

if len(resumo) != 1:
    st.error(
        "Era esperada uma única linha de resumo para esta edição. "
        "Confira o arquivo resumo_geral.csv."
    )
    st.stop()

indicadores = resumo.iloc[0]

aba_resumo, aba_classificacao, aba_mando = st.tabs(
    ["Resumo geral", "Classificação", "Casa e fora"]
)

with aba_resumo:
    st.subheader("Indicadores da base analisada")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Partidas", int(indicadores["total_partidas"]))
    c2.metric("Clubes", int(indicadores["total_clubes"]))
    c3.metric("Gols", int(indicadores["total_gols"]))
    c4.metric(
        "Gols por partida",
        f'{indicadores["media_gols_partida"]:.2f}',
    )

    st.subheader("Distribuição dos resultados")

    resultados = pd.DataFrame(
        {
            "Resultado": [
                "Vitória do mandante",
                "Vitória do visitante",
                "Empate",
            ],
            "Partidas": [
                indicadores["total_vitorias_mandante"],
                indicadores["total_vitorias_visitante"],
                indicadores["total_empates"],
            ],
        }
    ).set_index("Resultado")

    st.bar_chart(resultados)

with aba_classificacao:
    st.subheader("Classificação calculada")

    st.caption(
        "Critérios: pontos, vitórias, saldo de gols e gols pró, "
        "nessa ordem. Empates restantes mantêm a mesma posição."
    )

    tabela = classificacao.sort_values(
        "posicao_calculada",
        kind="stable",
    )

    if tabela["empate_residual"].eq(1).any():
        st.warning(
            "Há clubes empatados em todos os critérios aplicados. "
            "Esses clubes compartilham a mesma posição calculada."
        )

    nomes_colunas = {
        "posicao_calculada": "Posição",
        "clube": "Clube",
        "pontos": "Pontos",
        "jogos": "Jogos",
        "vitorias": "Vitórias",
        "empates": "Empates",
        "derrotas": "Derrotas",
        "gols_pro": "Gols pró",
        "gols_contra": "Gols contra",
        "saldo_gols": "Saldo",
        "aproveitamento_pct": "Aproveitamento (%)",
    }

    st.dataframe(
        tabela[list(nomes_colunas)].rename(columns=nomes_colunas),
        hide_index=True,
        use_container_width=True,
    )

with aba_mando:
    st.subheader("Comparação por clube")

    opcoes = mando.sort_values("clube")
    nomes_clubes = opcoes.set_index("club_id")["clube"].to_dict()

    clube_id = st.selectbox(
        "Selecione um clube",
        options=opcoes["club_id"].tolist(),
        format_func=lambda identificador: nomes_clubes[identificador],
    )

    clube = mando.loc[mando["club_id"] == clube_id].iloc[0]

    comparacao = pd.DataFrame(
        {
            "Mando": ["Em casa", "Fora de casa"],
            "Jogos": [
                clube["jogos_mandante"],
                clube["jogos_visitante"],
            ],
            "Pontos": [
                clube["pontos_mandante"],
                clube["pontos_visitante"],
            ],
            "Aproveitamento (%)": [
                clube["aproveitamento_mandante_pct"],
                clube["aproveitamento_visitante_pct"],
            ],
        }
    )

    st.dataframe(
        comparacao,
        hide_index=True,
        use_container_width=True,
    )

    st.caption("Comparação do aproveitamento percentual")
    st.bar_chart(
        comparacao.set_index("Mando")[["Aproveitamento (%)"]]
    )