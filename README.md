# Pipeline de Dados sobre Futebol (`pipeline_futebol`)

Projeto acadêmico prático para construção de um pipeline de dados sobre futebol, desenvolvido passo a passo utilizando **Python** e **SQL**, com arquitetura em camadas, geração de indicadores analíticos, testes automatizados com **pytest** e versionamento com Git.

---

## 🎯 Objetivo do Projeto

Construir e documentar um pipeline de engenharia de dados que:
1. Extraia e receba dados de partidas/estatísticas de futebol na camada bruta (**raw**).
2. Trate, limpe e padronize os dados na camada refinada (**refined**).
3. Modele agregações e indicadores analíticos na camada de consumo (**marts**).
4. Utilize consultas **SQL** e scripts **Python** nas transformações.
5. Garanta a qualidade e a integridade dos dados por meio de testes automatizados com **pytest**.
6. Mantenha um histórico transparente de desenvolvimento, registrando cada etapa, decisão e eventuais suposições ou correções da IA.

---

## 📊 Fonte de Dados e Escopo

- **Conjunto de Dados:** [Football Data from Transfermarkt](https://www.kaggle.com/datasets/davidcariboo/player-scores)
- **Autor:** David Cariboo ([repositório no GitHub: dcaribou/transfermarkt-datasets](https://github.com/dcaribou/transfermarkt-datasets))
- **Licença Declarada dos Dados:** **CC0: Public Domain (CC0-1.0)**, tanto na página do Kaggle quanto no repositório de origem no GitHub.
- **Arquivos Selecionados:** O pipeline utilizará exclusivamente os arquivos:
  - `games.csv`
  - `clubs.csv`
  - `competitions.csv`
- **Status das Atualizações e Recorte Temporal:** As atualizações da base estão pausadas pelo autor, com os dados disponíveis cobrindo o histórico até **6 de julho de 2026**.
- **Validação Estrutural e de Chaves:** As chaves de relacionamento identificadas preliminarmente (`competition_id`, `club_id`, `game_id`) não foram consideradas como validadas previamente; a consistência e integridade das chaves serão conferidas empiricamente nos dados reais após a etapa de download.

---

## 📁 Estrutura do Projeto

```text
pipeline_futebol/
├── data/
│   ├── raw/         # Dados brutos recebidos na fonte original (imutáveis)
│   ├── refined/     # Dados tratados, tipados e limpos
│   └── marts/       # Tabelas agregadas e indicadores de negócio prontos para análise
├── src/             # Código-fonte Python do pipeline (extração, carga e transformação)
├── sql/             # Consultas, scripts DDL e modelos de transformação SQL
├── tests/           # Testes automatizados com pytest (validação de dados e lógica)
├── .gitignore       # Arquivos e diretórios ignorados pelo Git
└── README.md        # Documentação geral do projeto
```

---

## 📋 Lista de Etapas do Projeto

- [x] **Etapa 1:** Criação da estrutura inicial de pastas e documentação (`data/`, `src/`, `sql/`, `tests/`, `.gitignore`, `.gitkeep` e `README.md`).
- [ ] **Etapa 2:** Inicialização do repositório Git e primeiro *commit* estrutural.
- [ ] **Etapa 3:** Escolha e definição do conjunto de dados (*dataset*) de futebol.
- [ ] **Etapa 4:** Configuração das dependências do projeto e ambiente virtual Python.
- [ ] **Etapa 5:** Ingestão dos dados brutos na camada `data/raw/`.
- [ ] **Etapa 6:** Tratamento e limpeza dos dados com destino à camada `data/refined/`.
- [ ] **Etapa 7:** Modelagem e cálculo de indicadores analíticos em SQL/Python para a camada `data/marts/`.
- [ ] **Etapa 8:** Desenvolvimento de testes automatizados com `pytest`.
- [ ] **Etapa 9:** Revisão final, validação de resultados e conclusão da documentação.

---

## 🛠️ Tecnologias Previstas

- **Python 3** (Processamento, automação e orquestração)
- **SQL / SQLite** (Modelagem relacional e consultas analíticas)
- **pytest** (Testes automatizados unitários e de qualidade de dados)
- **Git** (Controle de versão passo a passo)

---

## 🤖 Registro de Suposições, Erros e Correções da IA

Conforme diretriz do projeto acadêmico, esta seção registra ocorrências em que suposições, divergências de instruções ou falhas foram identificadas durante o desenvolvimento assistido por IA:

| ID | Situação Identificada | Suposição / Risco | Como foi Identificado | Ação Corretiva Realizada |
|---|---|---|---|---|
| 01 | Nomenclatura da pasta do projeto (`pipeline-futebol` vs. `pipeline_futebol`). | Desencontro de instruções entre orientação prévia do assistente e a pasta aberta. | Verificação do caminho do diretório antes de iniciar as operações. | Alinhamento com o usuário, confirmando o uso de `pipeline_futebol`. |
| 02 | Afirmação incorreta sobre a licença do repositório de origem (`dcaribou/transfermarkt-datasets`). | O assistente afirmou incorretamente que o repositório utilizava a licença MIT. | Conferência da licença exibida no repositório de origem, com auxílio de outro assistente, seguida de revisão pelo usuário. | Correção imediata no README, registrando que tanto o Kaggle quanto o repositório no GitHub declaram CC0-1.0. |
