# Pipeline de Dados sobre Futebol (`pipeline_futebol`)

Projeto acadêmico prático de engenharia de dados sobre futebol, desenvolvido passo a passo utilizando **Python** e **SQL** (via SQLite em memória), com arquitetura em camadas (*Raw*, *Refined* e *Marts*), geração de indicadores analíticos, validações matemáticas automatizadas e versionamento via Git.

---

## 🎯 Objetivo e Escopo do Projeto

O objetivo deste projeto é construir um pipeline de dados reprodutível, transparente e modular que:
1. Receba dados brutos de partidas e clubes na camada imutável (**raw**).
2. Trate, filtre, valide e enriqueça os dados na camada tratada (**refined**).
3. Modele e consolide indicadores analíticos e a classificação calculada na camada de consumo (**marts**), utilizando consultas SQL executadas em SQLite em memória (`:memory:`).
4. Assegure a qualidade e a integridade matemática por meio de testes automatizados com a biblioteca padrão (`unittest`), compatíveis com `pytest`.
5. Documente decisões metodológicas, limitações técnicas e o registro de suposições/correções da IA.

---

## 📊 Origem dos Dados e Obtenção dos Arquivos Brutos

- **Dataset utilizado, mantido por David Cariboo, com dados coletados do Transfermarkt:** [Football Data from Transfermarkt (Kaggle)](https://www.kaggle.com/datasets/davidcariboo/player-scores) e [repositório de origem no GitHub (dcaribou/transfermarkt-datasets)](https://github.com/dcaribou/transfermarkt-datasets).
- **Licença Declarada dos Dados:** **CC0: Public Domain (CC0-1.0)**, tanto na página do Kaggle quanto no repositório no GitHub.
- **Snapshot e Reprodutibilidade:** A reprodução exata dos resultados apresentados exige a utilização do mesmo snapshot dos dados brutos. A versão exata e a data de download dos arquivos em `data/raw/` não foram registradas. Portanto, não foi confirmada a correspondência desses arquivos com uma versão específica publicada pelo mantenedor. Não foram baixados novos dados durante esta revisão.
- **Instruções para Obtenção dos Dados Brutos:**
  1. Acesse a página do dataset no Kaggle ou no GitHub do mantenedor.
  2. Baixe os seguintes arquivos originais:
     - `games.csv`
     - `clubs.csv`
     - `competitions.csv`
  3. Copie os três arquivos exatamente para a pasta `data/raw/` deste projeto.
  4. Mantenha os arquivos brutos inalterados (a camada `data/raw/` é estritamente imutável para o pipeline).

---

## 🔍 Recorte Analítico e Mapeamento de Temporada

- **Recorte Adotado:** **Campeonato Brasileiro Série A – Edição Esportiva 2025**.
  - As 380 partidas do campeonato foram disputadas entre **29/03/2025 e 07/12/2025**.
  - O elenco de 20 clubes reflete a composição real da Série A de 2025 (incluindo clubes promovidos no final de 2024, como Mirassol, Santos, Sport e Ceará).
- **Distinção entre `temporada_origem` e `edicao_esportiva`:**
  - Na fonte original do Transfermarkt, o registro desta edição traz o campo `season = '2024'`. Levantamos a hipótese de que o Transfermarkt adota essa convenção para alinhar campeonatos de ano civil à temporada europeia (2024/2025), mas isso permanece estritamente como uma **hipótese não comprovada**.
  - Para garantir total clareza e rastreabilidade, a camada tratada separa explicitamente esses conceitos:
    - **`temporada_origem`**: preserva o valor bruto da fonte (`'2024'`).
    - **`edicao_esportiva`**: registra o ano civil efetivo da disputa (`2025`).
  - *Ressalva Metodológica:* Esse mapeamento decorre da verificação empírica deste recorte específico e **não deve ser extrapolado como regra geral (+1 ano)** para outras ligas ou temporadas sem auditoria prévia.

---

## 📁 Estrutura de Pastas do Projeto

```text
pipeline_futebol/
├── data/
│   ├── raw/                  # Dados brutos originais (games.csv, clubs.csv, competitions.csv)
│   ├── refined/              # Camada tratada: partidas_brasileirao_2025.csv
│   └── marts/                # Camada analítica: classificacao_calculada.csv, desempenho_mando.csv, resumo_geral.csv
├── src/
│   ├── config.py             # Configurações de caminhos, constantes e parâmetros do recorte
│   ├── transform_refined.py  # Script de transformação Raw -> Refined
│   └── build_marts.py        # Orquestrador da camada Marts via SQLite em memória
├── sql/
│   ├── marts_classificacao.sql   # Consulta SQL para classificação calculada
│   ├── marts_desempenho_mando.sql # Consulta SQL para métricas de mando de campo
│   └── marts_resumo_geral.sql     # Consulta SQL para resumo macro do campeonato
├── tests/
│   ├── test_refined.py       # Testes da camada refinada (datas, placares, integridade, confrontos)
│   └── test_marts.py         # Testes da camada analítica (invariantes, cruzamentos, empates residuais)
├── requirements-dev.txt      # Dependência de desenvolvimento declarada (pytest)
├── .gitignore                # Arquivos e diretórios ignorados pelo Git
└── README.md                 # Documentação geral e técnica do projeto
```

---

## 📈 Saídas Geradas e Critérios da Classificação Calculada

### 1. Camada Tratada (`data/refined/partidas_brasileirao_2025.csv`)
Contém as 380 partidas da edição de 2025, tipadas e enriquecidas com nomes oficiais dos clubes, resultado da partida (`VITORIA_MANDANTE`, `VITORIA_VISITANTE`, `EMPATE`), pontos conquistados por cada equipe (3, 1 ou 0) e saldos de gols.

### 2. Camada Analítica (*Marts*)
- **`data/marts/classificacao_calculada.csv` (20 clubes):**
  - **Critérios de Ordenação Implementados:**
    1. Total de Pontos Ganhos (decrescente)
    2. Número de Vitórias (decrescente)
    3. Saldo de Gols (decrescente)
    4. Gols Pró / Marcados (decrescente)
  - **Detecção de Empates Residuais:** Utiliza a função SQL `RANK()` para que equipes empatadas nos 4 critérios compartilhem rigorosamente a mesma colocação e recebam a flag `empate_residual = 1`. Não são aplicados critérios arbitrários de desempate por nome ou ID.
  - **Preservação de Atributos:** Mantém os campos estruturais `club_id` e `edicao_esportiva`.
- **`data/marts/desempenho_mando.csv` (20 clubes):**
  - Discrimina os 19 jogos em casa e os 19 jogos fora de cada equipe, comparando vitórias, empates, derrotas, gols pró/contra, saldo e aproveitamento percentual em cada mando. Mantém `club_id` e `edicao_esportiva`.
- **`data/marts/resumo_geral.csv` (1 linha consolidada):**
  - Totalizadores macro: 380 partidas, 20 clubes, 959 gols marcados (580 de mandantes e 379 de visitantes), média de 2,52 gols por partida, 191 vitórias de mandantes (50,26%), 90 de visitantes (23,68%) e 99 empates (26,05%).

---

## 🚀 Instruções de Execução

Todos os comandos devem ser executados a partir da **raiz do projeto** (`pipeline_futebol/`).

### 1. Executar a Transformação Raw → Refined
Lê os arquivos brutos em `data/raw/`, valida tipos e gera o CSV tratado:
```powershell
python src/transform_refined.py
```

### 2. Executar a Construção dos Marts Analíticos
Carrega os dados tratados no SQLite em memória, executa as consultas SQL e exporta os 3 CSVs analíticos:
```powershell
python src/build_marts.py
```

### 3. Executar a Suíte Completa de Testes Automatizados
Execução nativa via `unittest` (sem necessidade de instalar nenhum pacote adicional):
```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## ⚙️ Dependências: Biblioteca Padrão vs. Pytest Opcional

- **Execução Padrão (100% Nativa):** Todo o pipeline (extração, carga, modelagem em SQLite e testes automatizados) foi desenvolvido utilizando estritamente a **biblioteca padrão do Python 3** (`csv`, `pathlib`, `sqlite3`, `unittest`, `datetime`, `collections`). Nenhuma ferramenta ou pacote adicional precisa ser instalado para rodar o projeto do início ao fim.
- **Pytest (Opcional para Desenvolvimento / CI):** A dependência `pytest>=8.0.0` está formalmente declarada em [`requirements-dev.txt`](requirements-dev.txt). Caso você ou seu ambiente prefiram relatórios interativos com `pytest`, basta instalar:
  ```powershell
  pip install -r requirements-dev.txt
  pytest -v
  ```
  *Nota: Como os testes foram escritos com classes `unittest.TestCase`, o `pytest` os reconhece e executa nativamente sem necessidade de adaptação.*

---

## ⚠️ Limitações do Projeto

1. **Recorte Único:** O pipeline e suas regras foram construídos e validados empiricamente para o Campeonato Brasileiro Série A de 2025 (`BRA1` / `2024`). A aplicação direta a outras ligas ou copas requer validação prévia de integridade.
2. **Critérios de Desempate Parciais:** A classificação calculada aplica os quatro critérios implementados (Pontos, Vitórias, Saldo e Gols Pró). Não foram implementados critérios administrativos ou de regulamentos específicos (como confronto direto, cartões vermelhos/amarelos ou sorteio). Casos de empate nos 4 critérios são identificados transparentemente como empates residuais.
3. **Arquivos Gerados Ignorados pelo Git:** Por boas práticas de engenharia de software, o arquivo `.gitignore` ignora os CSVs gerados em `data/refined/*` e `data/marts/*`, garantindo que o repositório rastreie apenas código-fonte, consultas SQL, documentação e testes, permitindo a reprodução determinística dos dados a qualquer momento.
4. **Sobrescrita das Saídas:** A execução dos scripts `src/transform_refined.py` e `src/build_marts.py` substitui os arquivos gerados em execuções anteriores de forma idempotente.

---

## 🤖 Registro de Suposições, Erros e Correções da IA

Conforme diretriz do projeto acadêmico, esta seção documenta ocorrências em que suposições, divergências de instruções ou falhas foram identificadas durante o desenvolvimento assistido por IA:

| ID | Situação Identificada | Suposição / Risco | Como foi Identificado | Ação Corretiva Realizada |
|---|---|---|---|---|
| 01 | Nomenclatura da pasta do projeto (`pipeline-futebol` vs. `pipeline_futebol`). | Desencontro de instruções entre orientação prévia do assistente e a pasta aberta. | Verificação do caminho do diretório antes de iniciar as operações. | Alinhamento com o usuário, confirmando o uso de `pipeline_futebol`. |
| 02 | Afirmação incorreta sobre a licença do repositório de origem (`dcaribou/transfermarkt-datasets`). | O assistente afirmou incorretamente que o repositório utilizava a licença MIT. | Conferência da licença exibida no repositório de origem, com auxílio de outro assistente, seguida de revisão pelo usuário. | Correção imediata no README, registrando que tanto o Kaggle quanto o repositório no GitHub declaram CC0-1.0. |
