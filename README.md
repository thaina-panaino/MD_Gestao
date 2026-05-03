MD Gestão - Log de Engenharia & Diário de Bordo
    Autora: Thainá Panaino
    Foco: Cientista de Dados | Futura Machine Learning 
    Projeto: Sistema ERP para Microempreendedores de Personalizados

*Escopo Projeto de gestão para microempresas*

Um sistema robusto e elegante projetado para otimizar o fluxo de trabalho de quem trabalha com encomendas personalizadas. O foco é sair do controle manual e evoluir para uma gestão baseada em dados.

Inicialmente este projeto esta sendo desenvolvido para a MP Personalizados, com foco em otimizar tempo, organização e melhora na gestão.
O sistema se chama MD Gestão = Gestão de Métricas e Dados para a MP Personalizados

Como objetivos Principais:
   - Registrar pedidos: Controle total de fluxo de entrada.
   - Gestão de Clientes: Histórico de compras e contatos.
   - Financeiro: Acompanhamento de valores e faturamento.
   - Documentação: Geração de comprovantes em PDF.
   - Business Intelligence: Dashboard para visualização de métricas (Ticket Médio, Vendas por Período).
   
Stack Tecnológica escolhidas para o desenvolvimento do sistema:

| Área | Ferramenta | Uso |
| :--- | :--- | :--- |
| **Editor** | Visual Studio Code | Desenvolver o sistema |
| **Linguagem** | Python | Linguagem principal |
| **Versionamento** | Git + GitHub | Controle de versões e portfólio |
| **Banco de dados** | SQLite | Armazenar os dados |
| **Consulta banco** | SQL | Consultar dados do banco |
| **Manipulação de dados** | Pandas | Tratar e analisar dados |
| **Matemática / base ML** | NumPy | Cálculos numéricos |
| **Gráficos** | Matplotlib | Visualização de dados |
| **Machine Learning** | Scikit-learn | Modelos de previsão |
| **Exploração de dados** | Jupyter Notebook | Análise exploratória |
| **Dashboard** | Streamlit | Criar painel de dados |
| **Relatórios** | ReportLab | Gerar PDFs |

oadmap de Desenvolvimento e Escalabilidade

O projeto foi dividido em sprints estratégicas para garantir a evolução de um script simples para evolução.

Fase 1: Fundação e Automação de Dados (Em progresso 🟢)

    [x] Desenvolvimento dos primeiros códigos para notas em python.

    [x] Configuração de ambiente isolado com .venv no Linux Ubuntu.

    [x] Estruturação do fluxo de notas fiscais e persistência de dados.

    [x] Instalação e integração do Pandas e Streamlit para visualização.

    [ ] Refatoração do módulo de salvamento para garantir integridade sequencial.

Fase 2: Gestão 360º e Estruturação SQL (Próximo passo 🟡)

    [ ] Implantação do banco de dados SQLite utilizando SQL puro para consultas.

    [ ] Implementação do módulo de Gestão de Estoque (Insumos e Produtos).

    [ ] Cadastro unificado de clientes e fornecedores com histórico de relacionamento.

Fase 3: Business Intelligence e Reports (Planejamento 🔵)

    [ ] Desenvolvimento de Dashboards interativos com Matplotlib e Streamlit.

    [ ] Automação de relatórios financeiros em PDF com ReportLab.

    [ ] Cálculo automático de métricas como Ticket Médio e CAC (Custo de Aquisição de Cliente).

Fase 4: Machine Learning e Futuro (Visão L5 🚀)

    [ ] Análise Preditiva: Uso de Scikit-learn para prever meses de maior demanda na MP Personalizados.

    [ ] Clusterização: Agrupamento de perfis de clientes para marketing direcionado.

    [ ] Deploy: Migração para arquitetura em Nuvem (Cloud) para acesso remoto seguro.

-------------------------------------------------------------------------------
*Status de Desenvolvimento*

A prioridade inicial foi a organização do fluxo de vendas. Estabelecemos que o ponto de partida seria o módulo de Notas, permitindo o registro detalhado de cada transação.
   - Campos Estruturados: Nome do emissor, dados do cliente, data, hora e valores.
   - Automação e Integridade: Para mitigar erros humanos, implementamos a geração automática de numeração sequencial, garantindo que cada registro seja único e rastreável.
   - Reporting: Desenvolvimento de um protótipo de relatório para extração imediata de métricas básicas de desempenho.
    
Embora o projeto tenha nascido com foco estritamente financeiro, a evolução para uma ferramenta de gestão completa ocorreu após uma análise de requisitos com a Tania (proprietária da MP Personalizados).

Identificamos a necessidade de uma visão 360º do negócio, o que levou à expansão do escopo para incluir:
    Gestão de Estoque: Controle de produtos e insumos.
    Gestão de cadastros: Cadastro de clientes, produtos, fornecedores
    Gestão de Tempo: Monitoramento da eficiência produtiva.
    Business Intelligence: Transformação de dados brutos em decisões estratégicas para a empresa, informando atraves de dashboards completo
    
Rotina:
Atualmente tive que realizar a instalação do pandas, para isso precisei criar o ambiente .venv, para depois nele realizar a instalação do panadas (o .venv é uma pasta robusta que contém todo o motor do Python e as bibliotecas (Pandas, Streamlit, gerado pelo comando python3 -m venv .venv, para localizar abre o terminal no VS Code, Digita: source .venv/bin/activate, O Python "sabe" onde a pasta está e usa tudo o que instalado)
