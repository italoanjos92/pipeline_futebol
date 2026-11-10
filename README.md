# Pipeline de Dados sobre Futebol (`pipeline_futebol`)

Projeto acadêmico prático de engenharia de dados sobre futebol, desenvolvido com Python e SQL, utilizando SQLite em memória.

O projeto possui arquitetura em camadas (raw, refined e marts), indicadores analíticos, testes automatizados e um dashboard inicial em Streamlit.

---

## Objetivo e Escopo do Projeto

O objetivo é construir um pipeline transparente e modular que:

1. Leia arquivos brutos de partidas, clubes e competições na camada raw.
2. Filtre, transforme e enriqueça os dados na camada refined.
3. Gere indicadores e uma classificação calculada na camada marts, utilizando consultas SQL executadas em SQLite em memória (`:memory:`).
4. Verifique regras de negócio e consistência dos dados por meio de testes automatizados com `unittest`.
5. Disponibilize um dashboard em Streamlit para visualizar os marts existentes, sem alterar o pipeline ou recalcular a classificação.
6. Documente decisões metodológicas, limitações e suposições/correções identificadas durante o desenvolvimento assistido por IA.

O recorte utilizado é o Campeonato Brasileiro Série A, edição esportiva 2025.

A classificação produzida é calculada a partir dos resultados presentes nos arquivos locais. Não representa uma certificação da classificação oficial.

---

## Origem dos Dados e Obtenção dos Arquivos Brutos

### Fonte declarada

- Dataset: [Football Data from Transfermarkt (Kaggle)](https://www.kaggle.com/datasets/davidcariboo/player-scores).
- Mantenedor: David Cariboo.
- Repositório de origem: [dcaribou/transfermarkt-datasets](https://github.com/dcaribou/transfermarkt-datasets).
- Licença declarada: CC0: Public Domain (CC0-1.0), conforme as páginas do Kaggle e do repositório de origem.

### Snapshot e reprodutibilidade

A reprodução exata dos indicadores apresentados depende do mesmo snapshot dos dados brutos.

A versão e a data de download dos arquivos locais em `data/raw/` não foram registradas. Portanto, não foi confirmada a correspondência desses arquivos com uma publicação específica do mantenedor.

Não foram baixados novos dados durante esta revisão. Um novo download pode apresentar diferenças em relação aos arquivos utilizados no projeto.

### Como obter os arquivos

1. Acesse a página do dataset no Kaggle ou as instruções do repositório de origem.
2. Baixe os seguintes arquivos:
   - `games.csv`
   - `clubs.csv`
   - `competitions.csv`
3. Coloque os três arquivos na pasta `data/raw/`.
4. Preserve o conteúdo e os nomes originais dos arquivos.

Não há download automático na implementação atual.

A preservação dos arquivos brutos é uma regra do projeto. Não existe bloqueio técnico de escrita ou proteção por permissões implementado nessa pasta.

---

## Recorte Analítico e Mapeamento de Temporada

O projeto utiliza o seguinte filtro nos arquivos locais:

- `competition_id = "BRA1"`
- `season = "2024"`

O recorte é tratado no projeto como a edição esportiva 2025.

Para preservar a rastreabilidade, a camada refined mantém:

- `temporada_origem`: valor original da fonte, `"2024"`.
- `edicao_esportiva`: edição adotada para a análise, `2025`.

Esse mapeamento é específico dos arquivos locais analisados. Não deve ser generalizado como uma regra de adicionar um ano para outras competições, temporadas ou versões da fonte.

### Referências do snapshot local

- 380 partidas.
- 20 clubes.
- Datas entre 29/03/2025 e 07/12/2025.
- 38 partidas por clube.
- 19 partidas como mandante e 19 como visitante por clube.

Essas referências descrevem o recorte local utilizado no projeto, não qualquer versão futura do dataset.

---

## Estrutura de Pastas do Projeto

```text
pipeline_futebol/
├── data/
│   ├── raw/                     # games.csv, clubs.csv e competitions.csv
│   ├── refined/                 # partidas_brasileirao_2025.csv
│   └── marts/                   # CSVs analíticos
├── docs/
│   └── spec.md                  # Especificação do projeto, em revisão
├── src/
│   ├── config.py                # Configurações e caminhos
│   ├── transform_refined.py     # Transformação raw -> refined
│   └── build_marts.py           # Geração dos marts via SQLite em memória
├── sql/
│   ├── marts_classificacao.sql
│   ├── marts_desempenho_mando.sql
│   └── marts_resumo_geral.sql
├── tests/
│   ├── test_refined.py           # Testes da camada refined
│   └── test_marts.py             # Testes dos marts
├── app.py                       # Dashboard em Streamlit
├── requirements.txt             # pandas e Streamlit
├── requirements-dev.txt         # pytest opcional
├── .gitignore
└── README.md
```

Os CSVs brutos e gerados são ignorados pelo Git e não acompanham o repositório.

---

## Arquitetura

O processamento segue este fluxo:

```text
data/raw/
    |
    v
src/transform_refined.py
    |
    v
data/refined/partidas_brasileirao_2025.csv
    |
    v
src/build_marts.py + consultas em sql/
    |
    v
SQLite em memória
    |
    v
data/marts/
    |
    v
app.py — dashboard em Streamlit
```

O SQLite é utilizado em memória durante a construção dos marts. Não é necessário criar um banco de dados persistente para executar o dashboard.

O dashboard lê os CSVs dos marts existentes. Ele não executa automaticamente o pipeline nem altera os arquivos brutos, refinados ou analíticos.

---

## Saídas Geradas e Critérios da Classificação

### Camada refined

Arquivo:

```text
data/refined/partidas_brasileirao_2025.csv
```

Contém uma linha por partida, com identificadores, nomes dos clubes conforme a fonte, datas, placares, resultado, pontos e saldos de gols.

Valores de resultado:

- `VITORIA_MANDANTE`
- `VITORIA_VISITANTE`
- `EMPATE`

Regras de pontuação:

- Vitória: 3 pontos.
- Empate: 1 ponto.
- Derrota: 0 pontos.

A transformação não remove duplicatas automaticamente. A unicidade das partidas é verificada pelos testes.

### Classificação calculada

Arquivo:

```text
data/marts/classificacao_calculada.csv
```

Granularidade: uma linha por clube e edição esportiva.

Critérios de ordenação, todos em ordem decrescente:

1. Pontos.
2. Vitórias.
3. Saldo de gols.
4. Gols pró.

Clubes empatados nos quatro critérios recebem a mesma posição com a função SQL `RANK()` e são identificados com `empate_residual = 1`.

Nomes e identificadores não são utilizados como critérios esportivos de desempate.

O mart preserva `club_id` e `edicao_esportiva`.

### Desempenho por mando

Arquivo:

```text
data/marts/desempenho_mando.csv
```

Apresenta, por clube e edição esportiva:

- Jogos, vitórias, empates e derrotas como mandante e visitante.
- Gols pró, gols contra e saldo de gols em cada mando.
- Pontos e aproveitamento percentual em cada mando.
- Totais de jogos e pontos para reconciliação com a classificação.

### Resumo geral

Arquivo:

```text
data/marts/resumo_geral.csv
```

Referências do snapshot local:

| Indicador | Valor |
|---|---:|
| Partidas | 380 |
| Clubes | 20 |
| Gols | 959 |
| Gols de mandantes | 580 |
| Gols de visitantes | 379 |
| Média de gols por partida | 2,52 |
| Vitórias de mandantes | 191 |
| Vitórias de visitantes | 90 |
| Empates | 99 |
| Percentual de vitórias de mandantes | 50,26% |
| Percentual de vitórias de visitantes | 23,68% |
| Percentual de empates | 26,05% |

Os percentuais arredondados podem não somar exatamente 100%.

Esses indicadores são referências dos arquivos locais, não totais certificados contra uma fonte oficial.

---

## Dependências e Ambiente

### Pipeline e testes com unittest

O pipeline e os testes executados com `unittest` utilizam a biblioteca padrão do Python, incluindo módulos como `csv`, `pathlib`, `sqlite3` e `unittest`.

Essas etapas não exigem pandas ou Streamlit.

### Dashboard

As dependências do dashboard estão em `requirements.txt`:

```text
pandas>=2.0.0
streamlit>=1.35.0
```

### Pytest opcional

O arquivo `requirements-dev.txt` declara:

```text
pytest>=8.0.0
```

O pytest é uma alternativa para executar os testes, não uma exigência para a execução com unittest.

### Ambiente local utilizado

A execução acompanhada utilizou Windows, terminal Bash e Python 3.13.13.

Isso descreve o ambiente local utilizado, não uma garantia de compatibilidade com todas as versões do Python ou sistemas operacionais.

---

## Instruções de Execução

Execute os comandos a partir da raiz do projeto, `pipeline_futebol/`.

Os blocos abaixo são instruções para execução no terminal. Não é necessário executar novamente todas as etapas se o ambiente e os arquivos já estiverem preparados.

### 1. Criar e ativar o ambiente virtual

Para criar o ambiente, caso ainda não exista:

```bash
python -m venv .venv
```

No Windows com Bash, ative com:

```bash
source .venv/Scripts/activate
```

### 2. Disponibilizar os dados brutos

Confirme a presença dos três arquivos:

```text
data/raw/games.csv
data/raw/clubs.csv
data/raw/competitions.csv
```

Sem esses arquivos, a execução completa do pipeline não pode ser reproduzida.

### 3. Executar a transformação raw -> refined

```bash
python src/transform_refined.py
```

Essa etapa lê os arquivos brutos e gera:

```text
data/refined/partidas_brasileirao_2025.csv
```

### 4. Construir os marts

```bash
python src/build_marts.py
```

Essa etapa utiliza o refinado e as consultas SQL para gerar:

```text
data/marts/classificacao_calculada.csv
data/marts/desempenho_mando.csv
data/marts/resumo_geral.csv
```

A reexecução dos scripts sobrescreve os respectivos arquivos gerados.

### 5. Executar os testes com unittest

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

No Bash, para conferir o código de saída, execute imediatamente após os testes:

```bash
echo "Codigo de saida: $?"
```

### 6. Instalar as dependências do dashboard

Com o ambiente virtual ativo:

```bash
python -m pip install -r requirements.txt
```

### 7. Iniciar o dashboard

Com os três marts disponíveis:

```bash
python -m streamlit run app.py
```

Abra no navegador o endereço local informado pelo Streamlit.

Mantenha o terminal em execução enquanto utiliza o dashboard. Para encerrar a aplicação, pressione `Ctrl + C` nesse terminal.

### 8. Executar com pytest, opcionalmente

Para instalar:

```bash
python -m pip install -r requirements-dev.txt
```

Para executar:

```bash
python -m pytest -v
```

A execução com pytest ainda não foi conferida nesta rodada de validação.

---

## Dashboard

O dashboard inicial foi implementado no arquivo `app.py` e possui três abas.

### Resumo geral

- Total de partidas.
- Total de clubes.
- Total de gols.
- Média de gols por partida.
- Gráfico de vitórias de mandantes, vitórias de visitantes e empates.

### Classificação

- Tabela com a classificação calculada dos marts.
- Aviso para empates residuais nos critérios implementados.
- Identificação de que a classificação é calculada, não oficial.

### Casa e fora

- Seleção de clube.
- Comparação de jogos, pontos e aproveitamento como mandante e visitante.
- Gráfico de aproveitamento por mando.

O dashboard utiliza a edição esportiva configurada em `src/config.py`.

---

## Estado da Validação

### Testes automatizados

Na execução local de 10/11/2026, o comando com unittest apresentou:

```text
Ran 24 tests in 0.220s

OK
Codigo de saida: 0
```

Resultado:

- 24 testes executados.
- Nenhuma falha.
- Nenhum erro.
- Nenhum teste ignorado.
- Código de saída 0.

A suíte inclui casos sintéticos de regras de negócio e verificações dos arquivos locais, como:

- Unicidade das partidas.
- Coerência entre placares, pontos, resultados e saldos.
- Equilíbrio de mandos e confrontos entre clubes.
- Reconciliação de gols.
- Reconciliação entre classificação, desempenho por mando e resumo geral.
- Preservação de posições compartilhadas em empates residuais.

Um registro anterior apresentava divergência entre a mensagem `OK` e o código de saída informado pela ferramenta. A causa histórica não foi determinada, mas a divergência não se reproduziu nesta execução local.

### Conferências do dashboard

Já realizadas:

- A aplicação abriu no navegador em execução local.
- A seleção de outro clube atualizou a visualização da aba Casa e fora.

Ainda pendentes:

- Conferir a aba Classificação.
- Validar os indicadores e as visualizações contra os CSVs dos marts.
- Conferir as mensagens para arquivos ausentes ou dados incompatíveis.

A execução dos testes não equivale à validação completa do dashboard.

Também permanece pendente acompanhar uma nova execução completa do pipeline, dos arquivos brutos até a geração dos marts.

---

## Limitações do Projeto

1. O recorte é específico dos arquivos locais e do mapeamento `BRA1` / `2024` para a edição esportiva 2025.

2. A classificação utiliza apenas pontos, vitórias, saldo de gols e gols pró. Não reproduz integralmente critérios oficiais de desempate ou decisões administrativas.

3. Os CSVs brutos e gerados não acompanham o repositório. A reprodução exige fornecer os arquivos brutos nos caminhos esperados e executar o pipeline.

4. A versão e a data de download do snapshot local não foram registradas. Um novo download pode produzir indicadores diferentes.

5. Não há download automático nem atualização em tempo real.

6. A preservação dos arquivos brutos é uma convenção do projeto, sem bloqueio técnico de escrita.

7. A transformação não remove duplicatas automaticamente. Duplicatas devem ser investigadas.

8. Valores inválidos nos campos numéricos obrigatórios podem interromper a transformação.

9. Os arquivos gerados são sobrescritos, sem histórico próprio em disco.

10. Não há garantia de atualização conjunta e atômica de todos os CSVs.

11. O dashboard exige os marts previamente gerados e sua validação completa ainda está pendente.

12. Agentes autônomos não fazem parte da implementação atual.

---

## Documentação do Projeto

A especificação detalhada está em [docs/spec.md](docs/spec.md).

O documento permanece em revisão e registra contratos das camadas, indicadores, critérios de aceite, limitações e pendências.

---

## Registro de Suposições, Erros e Correções da IA

Esta seção registra ocorrências identificadas durante o desenvolvimento assistido por IA. Não representa um histórico completo de prompts.

| ID | Situação identificada | Suposição ou risco | Como foi identificado | Ação corretiva realizada |
|---|---|---|---|---|
| 01 | Nomenclatura da pasta do projeto: `pipeline-futebol` versus `pipeline_futebol`. | Desencontro entre instruções e a pasta utilizada. | Verificação do caminho do diretório. | Alinhamento com o usuário, confirmando `pipeline_futebol`. |
| 02 | Afirmação incorreta sobre a licença do repositório de origem. | O assistente afirmou que a licença era MIT. | Conferência da licença declarada na fonte, com auxílio de outro assistente e revisão pelo usuário. | Correção da documentação para CC0-1.0. |
| 03 | Referência duplicada e não confirmada sobre o snapshot local no README. | Associar os arquivos locais a uma publicação específica sem registro da versão ou da data de download. | Revisão do conteúdo do README. | Remoção da duplicação e da associação não comprovada. |
| 04 | Orientação para conferir um arquivo não rastreado com `git diff` comum. | Esperar que o comando mostrasse alterações de `docs/spec.md` antes de seu rastreamento. | Revisão da orientação durante a edição da spec. | Correção da orientação e conferência do conteúdo fornecido pelo usuário. |
| 05 | Documentação continuava tratando o dashboard como não implementado. | Manter divergência entre o código existente e a descrição do projeto. | Leitura completa da spec. | Atualização das referências ao dashboard, preservando as validações pendentes. |

Não devem ser inventados prompts históricos, resultados de execução ou agentes que não foram implementados.