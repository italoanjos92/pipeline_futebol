-- ==============================================================================
-- Mart: Classificação Calculada do Campeonato Brasileiro Série A (Edição 2025)
--
-- Regras e Critérios de Ordenação:
--   1. Total de Pontos (decrescente)
--   2. Número de Vitórias (decrescente)
--   3. Saldo de Gols (decrescente)
--   4. Gols Pró / Marcados (decrescente)
--
-- Detecção de Empates Residuais:
--   - Clubes com idênticos pontos, vitórias, saldo e gols pró compartilham a
--     mesma posição (via função RANK()) e recebem flag empate_residual = 1.
--   - Não são aplicados critérios arbitrários de desempate por nome ou ID.
--
-- Preservação de atributos: club_id e edicao_esportiva são mantidos na saída.
-- ==============================================================================

WITH partidas_unificadas AS (
    -- Perspectiva do Clube como Mandante
    SELECT
        edicao_esportiva,
        id_mandante AS club_id,
        nome_mandante AS clube,
        gols_mandante AS gols_pro,
        gols_visitante AS gols_contra,
        CASE WHEN pontos_mandante = 3 THEN 1 ELSE 0 END AS vitoria,
        CASE WHEN pontos_mandante = 1 THEN 1 ELSE 0 END AS empate,
        CASE WHEN pontos_mandante = 0 THEN 1 ELSE 0 END AS derrota,
        pontos_mandante AS pontos
    FROM refined_partidas

    UNION ALL

    -- Perspectiva do Clube como Visitante
    SELECT
        edicao_esportiva,
        id_visitante AS club_id,
        nome_visitante AS clube,
        gols_visitante AS gols_pro,
        gols_mandante AS gols_contra,
        CASE WHEN pontos_visitante = 3 THEN 1 ELSE 0 END AS vitoria,
        CASE WHEN pontos_visitante = 1 THEN 1 ELSE 0 END AS empate,
        CASE WHEN pontos_visitante = 0 THEN 1 ELSE 0 END AS derrota,
        pontos_visitante AS pontos
    FROM refined_partidas
),

totais_agregados AS (
    SELECT
        edicao_esportiva,
        club_id,
        clube,
        COUNT(*) AS jogos,
        SUM(vitoria) AS vitorias,
        SUM(empate) AS empates,
        SUM(derrota) AS derrotas,
        SUM(gols_pro) AS gols_pro,
        SUM(gols_contra) AS gols_contra,
        SUM(gols_pro) - SUM(gols_contra) AS saldo_gols,
        SUM(pontos) AS pontos,
        ROUND((CAST(SUM(pontos) AS REAL) / (COUNT(*) * 3.0)) * 100.0, 2) AS aproveitamento_pct
    FROM partidas_unificadas
    GROUP BY
        edicao_esportiva,
        club_id,
        clube
)

SELECT
    RANK() OVER (
        ORDER BY
            pontos DESC,
            vitorias DESC,
            saldo_gols DESC,
            gols_pro DESC
    ) AS posicao_calculada,
    edicao_esportiva,
    club_id,
    clube,
    jogos,
    vitorias,
    empates,
    derrotas,
    gols_pro,
    gols_contra,
    saldo_gols,
    pontos,
    aproveitamento_pct,
    CASE
        WHEN COUNT(*) OVER (
            PARTITION BY pontos, vitorias, saldo_gols, gols_pro
        ) > 1 THEN 1
        ELSE 0
    END AS empate_residual
FROM totais_agregados
ORDER BY
    posicao_calculada ASC;
