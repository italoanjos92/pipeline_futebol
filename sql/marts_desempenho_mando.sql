-- ==============================================================================
-- Mart: Desempenho por Mando de Campo (Edição 2025)
--
-- Agrega as estatísticas de cada clube discriminando o rendimento em casa
-- (mandante) e fora de casa (visitante), permitindo análise comparativa de mando.
--
-- Preservação de atributos: club_id e edicao_esportiva são mantidos na saída.
-- ==============================================================================

WITH mandante_stats AS (
    SELECT
        edicao_esportiva,
        id_mandante AS club_id,
        nome_mandante AS clube,
        COUNT(*) AS jogos_mandante,
        SUM(CASE WHEN pontos_mandante = 3 THEN 1 ELSE 0 END) AS vitorias_mandante,
        SUM(CASE WHEN pontos_mandante = 1 THEN 1 ELSE 0 END) AS empates_mandante,
        SUM(CASE WHEN pontos_mandante = 0 THEN 1 ELSE 0 END) AS derrotas_mandante,
        SUM(gols_mandante) AS gols_pro_mandante,
        SUM(gols_visitante) AS gols_contra_mandante,
        SUM(saldo_gols_mandante) AS saldo_gols_mandante,
        SUM(pontos_mandante) AS pontos_mandante,
        ROUND((CAST(SUM(pontos_mandante) AS REAL) / (COUNT(*) * 3.0)) * 100.0, 2) AS aproveitamento_mandante_pct
    FROM refined_partidas
    GROUP BY
        edicao_esportiva,
        id_mandante,
        nome_mandante
),

visitante_stats AS (
    SELECT
        edicao_esportiva,
        id_visitante AS club_id,
        nome_visitante AS clube,
        COUNT(*) AS jogos_visitante,
        SUM(CASE WHEN pontos_visitante = 3 THEN 1 ELSE 0 END) AS vitorias_visitante,
        SUM(CASE WHEN pontos_visitante = 1 THEN 1 ELSE 0 END) AS empates_visitante,
        SUM(CASE WHEN pontos_visitante = 0 THEN 1 ELSE 0 END) AS derrotas_visitante,
        SUM(gols_visitante) AS gols_pro_visitante,
        SUM(gols_mandante) AS gols_contra_visitante,
        SUM(saldo_gols_visitante) AS saldo_gols_visitante,
        SUM(pontos_visitante) AS pontos_visitante,
        ROUND((CAST(SUM(pontos_visitante) AS REAL) / (COUNT(*) * 3.0)) * 100.0, 2) AS aproveitamento_visitante_pct
    FROM refined_partidas
    GROUP BY
        edicao_esportiva,
        id_visitante,
        nome_visitante
)

SELECT
    m.edicao_esportiva,
    m.club_id,
    m.clube,
    m.jogos_mandante,
    m.vitorias_mandante,
    m.empates_mandante,
    m.derrotas_mandante,
    m.gols_pro_mandante,
    m.gols_contra_mandante,
    m.saldo_gols_mandante,
    m.pontos_mandante,
    m.aproveitamento_mandante_pct,
    v.jogos_visitante,
    v.vitorias_visitante,
    v.empates_visitante,
    v.derrotas_visitante,
    v.gols_pro_visitante,
    v.gols_contra_visitante,
    v.saldo_gols_visitante,
    v.pontos_visitante,
    v.aproveitamento_visitante_pct,
    (m.jogos_mandante + v.jogos_visitante) AS total_jogos,
    (m.pontos_mandante + v.pontos_visitante) AS total_pontos
FROM mandante_stats m
JOIN visitante_stats v
    ON m.club_id = v.club_id
   AND m.edicao_esportiva = v.edicao_esportiva
ORDER BY
    total_pontos DESC,
    m.pontos_mandante DESC,
    v.pontos_visitante DESC;
