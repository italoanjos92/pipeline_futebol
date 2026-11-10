# Especificação do Pipeline de Dados — Brasileirão 2025

Projeto: pipeline_futebol

## Status e natureza do documento

Este documento foi elaborado após a implementação inicial do pipeline e dos
testes, como consolidação do estado existente. Não representa uma especificação
escrita antes dessa implementação.

Status: em revisão.

Após sua aprovação, passa a ser o contrato para alterações futuras.
Funcionalidades novas devem ter suas decisões registradas e aprovadas antes
da implementação.

As contagens e os indicadores deste documento são referências do snapshot local
utilizado no projeto. Não devem ser apresentados como valores universais de
qualquer versão da fonte.

---

## 1. Objetivo e escopo

### 1.1 Objetivo

Construir um pipeline de dados modular, com Python e SQL, que leia arquivos
brutos de partidas de futebol, produza uma camada refinada e gere tabelas
analíticas para responder perguntas sobre o Brasileirão 2025.

Os marts são processados com SQLite em memória e exportados para CSV.

### 1.2 Escopo implementado

- Campeonato Brasileiro Série A, edição esportiva 2025.
- Recorte local com 380 partidas e 20 clubes.
- Camadas raw, refined e marts.
- Classificação calculada com quatro critérios estatísticos.
- Desempenho por mando de campo.
- Resumo dos resultados e gols da competição.
- Testes automatizados de regras de negócio e reconciliação.

### 1.3 Dashboard inicial implementado

Dashboard em Streamlit, no arquivo app.py, para visualizar os marts existentes.

Possui três abas: Resumo geral, Classificação e Casa e fora.
Na aba Casa e fora, permite selecionar um clube.

A aplicação foi aberta localmente e a troca de clube foi conferida.
A validação completa do dashboard ainda está pendente.

### 1.4 Fora do escopo da implementação atual

- Outras competições ou edições.
- Estatísticas individuais de atletas.
- Dados financeiros e transferências.
- Download automático dos dados.
- Atualização em tempo real.
- Agentes autônomos.
- Reprodução integral dos critérios oficiais de desempate.

---

## 2. Perguntas de negócio

1. Qual é a classificação calculada com pontos, vitórias, saldo de gols
   e gols pró? Existem empates residuais nesses critérios?

2. Como o desempenho dos clubes varia entre partidas como mandante
   e visitante?

3. Quantos gols foram registrados e qual é a média por partida?

4. Como os resultados se distribuem entre vitórias de mandantes,
   vitórias de visitantes e empates?

5. Quais clubes apresentam os maiores e menores totais de gols pró,
   gols contra e saldo de gols?

A classificação calculada é uma análise dos resultados presentes na fonte,
não uma certificação da classificação oficial.

---

## 3. Fonte e recorte dos dados

### 3.1 Fonte declarada

- Dataset: Football Data from Transfermarkt.
- Distribuição: Kaggle.
- Repositório de origem:
  https://github.com/dcaribou/transfermarkt-datasets
- Licença declarada na documentação do projeto: CC0-1.0.

### 3.2 Arquivos de entrada

Os arquivos devem estar disponíveis em data/raw/:

- games.csv: partidas, datas, placares e identificadores.
- clubs.csv: identificadores e nomes dos clubes.
- competitions.csv: cadastro das competições.

Não há download automático na implementação atual.

### 3.3 Filtro aplicado

- competition_id = "BRA1"
- season = "2024"

O projeto preserva a distinção:

- temporada_origem: "2024", conforme o rótulo da fonte.
- edicao_esportiva: 2025, conforme o recorte esportivo adotado.

Esse mapeamento é específico dos arquivos locais analisados. Não deve
ser generalizado para outras versões ou competições sem investigação.

### 3.4 Referências do snapshot local

- games.csv: 88.958 registros.
- clubs.csv: 796 registros.
- competitions.csv: 65 registros.
- Recorte refinado: 380 partidas.
- Intervalo de datas adotado: 2025-03-29 a 2025-12-07.

Essas referências devem ser conferidas quando os arquivos forem substituídos.

### 3.5 Limitação de identificação do snapshot

A versão e a data de download dos arquivos locais não foram registradas.
Não é possível afirmar a qual publicação da fonte eles correspondem.

A reprodução exata dos indicadores depende do mesmo snapshot local.

Novos arquivos devem ser avaliados separadamente antes de substituir os
dados utilizados nesta entrega.

---

## 4. Arquitetura

Fluxo implementado:

    data/raw/
      games.csv
      clubs.csv
      competitions.csv
            |
            v
    src/transform_refined.py
            |
            v
    data/refined/
      partidas_brasileirao_2025.csv
            |
            v
    src/build_marts.py
      SQLite em memória
      consultas em sql/
            |
            v
    data/marts/
      classificacao_calculada.csv
      desempenho_mando.csv
      resumo_geral.csv

Fluxo do dashboard implementado:

    CSVs dos marts
            |
            v
    app.py
      dashboard em Streamlit
      leitura dos marts existentes

Arquivos de suporte:

- src/config.py: configurações e caminhos.
- tests/test_refined.py: testes da transformação e do refinado.
- tests/test_marts.py: testes dos marts.
- app.py: dashboard em Streamlit para leitura e visualização dos marts.
- requirements.txt: dependências do dashboard, pandas e Streamlit.

A arquitetura atual não utiliza banco DuckDB persistente.
Não é necessário migrar o processamento existente para criar o dashboard.

---

## 5. Contrato da camada raw

1. Os arquivos brutos devem preservar o conteúdo recebido da fonte.

2. O pipeline deve apenas ler data/raw/, sem alterar, sobrescrever
   ou excluir os arquivos.

3. A imutabilidade é uma regra do projeto. Não há bloqueio técnico
   de escrita implementado.

4. Os nomes originais dos arquivos e das colunas são preservados.

5. Os dados não acompanham o versionamento do código, conforme
   as regras do .gitignore.

6. A ausência de um arquivo necessário provoca falha de leitura.
   Não se presume validação prévia de todos os arquivos nem
   diagnóstico personalizado.

---

## 6. Contrato da camada refined

### 6.1 Saída e granularidade

Arquivo:

data/refined/partidas_brasileirao_2025.csv

Granularidade:

Uma linha por partida do recorte selecionado.

Referência de volume:

380 registros e 17 colunas.

### 6.2 Colunas

Os tipos abaixo representam o contrato lógico dos valores.
CSV não armazena um esquema de tipos como uma tabela de banco.

| Coluna | Tipo lógico | Descrição |
|---|---|---|
| game_id | inteiro | Identificador da partida |
| temporada_origem | texto | Rótulo original da temporada |
| edicao_esportiva | inteiro | Ano esportivo adotado |
| competition_id | texto | Identificador da competição |
| data_partida | texto ISO | Data no formato YYYY-MM-DD |
| rodada | texto | Rodada conforme a fonte |
| id_mandante | inteiro | Identificador do mandante |
| nome_mandante | texto | Nome do mandante |
| id_visitante | inteiro | Identificador do visitante |
| nome_visitante | texto | Nome do visitante |
| gols_mandante | inteiro | Gols do mandante |
| gols_visitante | inteiro | Gols do visitante |
| resultado_partida | texto | Resultado derivado do placar |
| pontos_mandante | inteiro | Pontos do mandante |
| pontos_visitante | inteiro | Pontos do visitante |
| saldo_gols_mandante | inteiro | Saldo do mandante |
| saldo_gols_visitante | inteiro | Saldo do visitante |

### 6.3 Regras de transformação

1. Selecionar exclusivamente o recorte BRA1 / 2024.

2. Obter os nomes dos clubes pelo mapeamento club_id -> name de clubs.csv.

3. Na ausência de correspondência no cadastro de clubes, utilizar o nome
   registrado na partida como fallback.

4. Converter identificadores numéricos e placares com int().

5. Representar as datas no formato ISO YYYY-MM-DD.

6. Derivar resultado, pontos e saldos a partir dos placares.

7. Ordenar por data_partida e, em seguida, por game_id.

### 6.4 Resultados e pontos

Vitória do mandante:

- resultado_partida = VITORIA_MANDANTE
- pontos_mandante = 3
- pontos_visitante = 0

Vitória do visitante:

- resultado_partida = VITORIA_VISITANTE
- pontos_mandante = 0
- pontos_visitante = 3

Empate:

- resultado_partida = EMPATE
- pontos_mandante = 1
- pontos_visitante = 1

Saldos:

- saldo_gols_mandante = gols_mandante - gols_visitante
- saldo_gols_visitante = gols_visitante - gols_mandante

### 6.5 Nulos e conversões

Valores vazios ou não convertíveis nos campos numéricos obrigatórios
provocam falha de conversão.

Não substituir silenciosamente placares ausentes por zero.

Não transformar falhas de conversão em nulos para continuar a execução.

A implementação atual não possui diagnóstico personalizado para todas
essas falhas.

### 6.6 Duplicatas

A transformação atual não remove duplicatas.

A unicidade de game_id no resultado é verificada pelos testes.
Duplicatas devem ser investigadas, não descartadas por regra implícita.

### 6.7 Reexecução

O arquivo gerado é sobrescrito.

Com os mesmos arquivos de entrada e a mesma versão do código, a execução
deve produzir os mesmos registros e a mesma ordenação.

A sobrescrita não mantém histórico dos arquivos gerados.

---

## 7. Contrato dos marts

### 7.1 Processamento

- Entrada: CSV refinado.
- Motor: SQLite em memória, com conexão :memory:.
- Consultas: arquivos SQL do projeto.
- Saída: CSVs em data/marts/.
- Reexecução: sobrescrita dos CSVs gerados.

Falhas de abertura de arquivos e execução SQL interrompem o processamento.
Não se presume recuperação automática nem publicação atômica de todos os marts.

### 7.2 classificacao_calculada

Arquivo:

data/marts/classificacao_calculada.csv

Granularidade:

Uma linha por clube e edição esportiva.

Referência:

20 registros.

Colunas:

- posicao_calculada
- edicao_esportiva
- club_id
- clube
- jogos
- vitorias
- empates
- derrotas
- gols_pro
- gols_contra
- saldo_gols
- pontos
- aproveitamento_pct
- empate_residual

Ordem dos critérios:

1. pontos, decrescente.
2. vitorias, decrescente.
3. saldo_gols, decrescente.
4. gols_pro, decrescente.

Empates residuais:

- Clubes iguais nos quatro critérios recebem a mesma posição com RANK().
- empate_residual indica igualdade nos quatro critérios.
- Nome e identificador não podem decidir a posição esportiva.
- Critérios adicionais não são implementados.

### 7.3 desempenho_mando

Arquivo:

data/marts/desempenho_mando.csv

Granularidade:

Uma linha por clube e edição esportiva.

Referência:

20 registros.

Identificação:

- edicao_esportiva
- club_id
- clube

Bloco mandante:

- jogos_mandante
- vitorias_mandante
- empates_mandante
- derrotas_mandante
- gols_pro_mandante
- gols_contra_mandante
- saldo_gols_mandante
- pontos_mandante
- aproveitamento_mandante_pct

Bloco visitante:

- jogos_visitante
- vitorias_visitante
- empates_visitante
- derrotas_visitante
- gols_pro_visitante
- gols_contra_visitante
- saldo_gols_visitante
- pontos_visitante
- aproveitamento_visitante_pct

Totais de controle:

- total_jogos
- total_pontos

Os totais por clube devem reconciliar com classificacao_calculada
pela chave (club_id, edicao_esportiva).

### 7.4 resumo_geral

Arquivo:

data/marts/resumo_geral.csv

Granularidade:

Uma linha por edição esportiva.

Colunas e referências do snapshot local:

| Coluna | Referência |
|---|---|
| edicao_esportiva | 2025 |
| competition_id | BRA1 |
| total_partidas | 380 |
| total_clubes | 20 |
| total_gols | 959 |
| total_gols_mandante | 580 |
| total_gols_visitante | 379 |
| media_gols_partida | 2.52 |
| total_vitorias_mandante | 191 |
| total_vitorias_visitante | 90 |
| total_empates | 99 |
| pct_vitorias_mandante | 50.26 |
| pct_vitorias_visitante | 23.68 |
| pct_empates | 26.05 |

Os percentuais arredondados podem não somar exatamente 100.

---

## 8. Definição dos indicadores

### 8.1 Pontos

pontos = 3 * vitorias + empates

### 8.2 Jogos

jogos = vitorias + empates + derrotas

### 8.3 Saldo de gols

saldo_gols = gols_pro - gols_contra

### 8.4 Aproveitamento

aproveitamento_pct = pontos / (3 * jogos) * 100

Apresentação com duas casas decimais.

Referências para a edição completa:

- 38 jogos por clube.
- 19 jogos como mandante.
- 19 jogos como visitante.

### 8.5 Média de gols

media_gols_partida = total_gols / total_partidas

Apresentação com duas casas decimais.

### 8.6 Percentual de resultado

percentual = quantidade_do_resultado / total_partidas * 100

Calcular separadamente:

- vitória do mandante.
- vitória do visitante.
- empate.

Apresentação com duas casas decimais.

---

## 9. Critérios de aceite

| Código | Critério | Referência |
|---|---|---|
| CA-01 | Total de partidas refinadas | 380 |
| CA-02 | game_id distintos | 380, sem duplicatas |
| CA-03 | Clubes participantes | 20 |
| CA-04 | Referências de clubes e competição | Presentes nas tabelas de apoio |
| CA-05 | Mandos por clube | 19 em casa e 19 fora |
| CA-06 | Pares de clubes | 190, com uma partida em cada mando |
| CA-07 | Placares | Inteiros, não nulos e não negativos |
| CA-08 | Reconciliação de gols | Soma de GP = soma de GC = 959 |
| CA-09 | Reconciliação de saldos | Soma dos saldos = 0 |
| CA-10 | Reconciliação entre marts | Jogos e pontos iguais por clube e edição |
| CA-11 | Empates residuais | Caso sintético preserva a mesma posição |
| CA-12 | Suíte automatizada | Sem falhas, erros ou testes ignorados |

Os critérios são requisitos de validação, não uma declaração de que uma
nova execução já foi realizada.

---

## 10. Testes automatizados

Inventário informado pela inspeção dos arquivos:

- tests/test_refined.py: 15 testes.
- tests/test_marts.py: 9 testes.
- Total: 24 testes.

### 10.1 Refined

1. test_formula_pontos_vitoria_mandante
2. test_formula_pontos_vitoria_visitante
3. test_formula_pontos_empate
4. test_transform_single_match_caso_sintetico_valido
5. test_transform_single_match_filtra_fora_do_recorte
6. test_total_registros_e_chaves_unicas
7. test_mapeamento_temporada_e_edicao
8. test_datas_validas_e_intervalo
9. test_gols_inteiros_e_nao_negativos
10. test_coerencia_placar_pontos_resultado_e_saldo
11. test_referencias_em_tabelas_de_apoio
12. test_reconciliacao_gols
13. test_equilibrio_por_ids_dos_clubes
14. test_confronto_em_cada_mando_por_par_de_clubes
15. test_ordenacao_cronologica

### 10.2 Marts

1. test_classificacao_detecta_empate_residual_sem_desempate_arbitrario
2. test_formula_pontos_classificacao
3. test_total_jogos_classificacao
4. test_reconciliacao_gols_pro_e_contra
5. test_soma_dos_saldos_igual_a_zero
6. test_desempenho_mando_soma_igual_ao_total
7. test_cruzamento_mando_e_classificacao_por_clube
8. test_ordenacao_criterios_classificacao
9. test_reconciliacao_resumo_geral

### 10.3 Execução

Comando utilizado no projeto:

    python -m unittest discover -s tests -p "test_*.py" -v

Executar com o ambiente Python destinado ao projeto.

A aprovação deve considerar:

- total de testes executados.
- ausência de falhas.
- ausência de erros.
- ausência de testes ignorados.
- código de saída do Python igual a zero.

Na execução local de 10/11/2026, foram executados 24 testes em 0.220s,
todos aprovados, sem falhas, erros ou testes ignorados.
O código de saída do Python, conferido imediatamente após a execução,
foi 0.

O registro anterior apresentava divergência entre a mensagem OK e o código
de saída informado pela ferramenta. A causa histórica não foi determinada,
mas a divergência não se reproduziu nesta execução local.

Esse resultado valida a suíte atual com os arquivos locais disponíveis.
Não equivale à validação completa do dashboard nem à certificação dos
dados contra a classificação oficial.
---

## 11. Limitações

1. O recorte é específico dos arquivos locais e do mapeamento BRA1 / 2024
   para a edição esportiva 2025.

2. A classificação usa apenas os quatro critérios documentados.
   Não reproduz integralmente regras oficiais nem decisões administrativas.

3. Os CSVs brutos e gerados não acompanham o repositório.

4. A reprodução exige os três arquivos brutos nos caminhos esperados.

5. Não há download automático.

6. Sem identificação da versão original do snapshot, um novo download
   pode produzir resultados diferentes.

7. A camada refined não possui deduplicação automática.

8. Valores numéricos obrigatórios inválidos provocam falha de conversão.

9. A proteção de data/raw/ é convencional, não um bloqueio de permissões.

10. Os arquivos gerados são sobrescritos, sem histórico próprio em disco.

11. Não há garantia de atualização conjunta e atômica de todos os CSVs.

12.  O dashboard inicial foi implementado em Streamlit e consome os marts
    existentes. A validação completa e a atualização do README ainda
    estão pendentes.

---

## 12. Próximas etapas

### 12.1 Dashboard

A versão inicial foi implementada em Streamlit no arquivo app.py.

Funcionalidades implementadas:

- Aba Resumo geral com indicadores e distribuição dos resultados.
- Aba Classificação com a classificação calculada dos marts.
- Aba Casa e fora com seleção de clube e comparação por mando.

Conferências realizadas:

- A aplicação abriu no navegador em execução local.
- A seleção de outro clube atualizou a visualização da aba Casa e fora.

Pendências:

- Conferir a aba Classificação.
- Validar os indicadores e as visualizações contra os CSVs dos marts.
- Conferir as mensagens para arquivos ausentes ou dados incompatíveis.
- Atualizar as instruções de instalação e execução no README.

O dashboard deve consumir os marts existentes e não alterar dados brutos,
dados refinados ou resultados do pipeline.

A implementação não deve inventar indicadores ausentes nem recalcular
regras de classificação de forma diferente dos marts.

### 12.2 Uso de IA

Documentar somente o uso real de IA no projeto:

- tarefas apoiadas.
- prompts efetivamente utilizados.
- decisões propostas.
- erros e suposições identificados.
- consultas e testes utilizados para validação.
- correções realizadas.

Não inventar prompts históricos, resultados de execução ou agentes que
não foram implementados.

### 12.3 Fechamento da entrega

- Suíte atual conferida com os dados locais: 24 testes aprovados e
  código de saída 0 em 10/11/2026.
- Pendente: conferir a execução completa do pipeline, da leitura dos
  arquivos brutos à geração dos marts.
- Concluir a validação do dashboard inicial já implementado.
- Atualizar as instruções de execução no README.
- Revisar as alterações antes de preparar arquivos para commit.
- Registrar commits e realizar push apenas após autorização.