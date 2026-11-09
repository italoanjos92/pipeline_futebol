-- ==============================================================================
-- Mart: Resumo Geral de Indicadores da Edição (Brasileirão 2025)
--
-- Consolida os principais indicadores macro do campeonato: total de jogos,
-- total e média de gols, distribuição de vitórias mandante/visitante e empates.
-- ==============================================================================

WITH base_clubes AS (
    SELECT id_mandante AS club_id FROM refined_partidas
    UNION
    SELECT id_visitante AS club_id FROM refined_partidas
)

SELECT
    edicao_esportiva,
    competition_id,
    COUNT(*) AS total_partidas,
    (SELECT COUNT(*) FROM base_clubes) AS total_clubes,
    SUM(gols_mandante + gols_visitante) AS total_gols,
    SUM(gols_mandante) AS total_gols_mandante,
    SUM(gols_visitante) AS total_gols_visitante,
    ROUND(CAST(SUM(gols_mandante + gols_visitante) AS REAL) / COUNT(*), 2) AS media_gols_partida,
    SUM(CASE WHEN resultado_partida = 'VITORIA_MANDANTE' THEN 1 ELSE 0 END) AS total_vitorias_mandante,
    SUM(CASE WHEN resultado_partida = 'VITORIA_VISITANTE' THEN 1 ELSE 0 END) AS total_vitorias_visitante,
    SUM(CASE WHEN resultado_partida = 'EMPATE' THEN 1 ELSE 0 END) AS total_empates,
    ROUND((CAST(SUM(CASE WHEN resultado_partida = 'VITORIA_MANDANTE' THEN 1 ELSE 0 END) AS REAL) / COUNT(*)) * 100.0, 2) AS pct_vitorias_mandante,
    ROUND((CAST(SUM(CASE WHEN resultado_partida = 'VITORIA_VISITANTE' THEN 1 ELSE 0 END) AS REAL) / COUNT(*)) * 100.0, 2) AS pct_vitorias_visitante,
    ROUND((CAST(SUM(CASE WHEN resultado_partida = 'EMPATE' THEN 1 ELSE 0 END) AS REAL) / COUNT(*)) * 100.0, 2) AS pct_empates
FROM refined_partidas
GROUP BY
    edicao_esportiva,
    competition_id;
