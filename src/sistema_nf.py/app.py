import streamlit as st
import pandas as pd
from database import conectar, criar_tabelas, executar_query, registrar_log, buscar_dados
from datetime import datetime
import re
from fpdf import FPDF
import plotly.express as px 

# --- CONFIGURACAO DE INTERFACE ---
st.set_page_config(page_title="MD Gestao Enterprise", layout="wide")

# Inicializacao automatica das tabelas no banco de dados
criar_tabelas()

# --- CODIGO DE EMERGENCIA PARA ACESSO INICIAL ---
try:
    # Cria um usuario padrão caso o banco esteja zerado
    executar_query("INSERT OR IGNORE INTO usuarios (usuario, senha) VALUES (?, ?)", ("admin", "123"))
except:
    pass

# Inicializacao do estado do carrinho de compras
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- FUNCOES DE APOIO E GERACAO DE DOCUMENTOS ---
def gerar_pdf_vendas(df):
    """Gera um relatorio geral de vendas em formato PDF."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "Relatorio de Vendas - MD Gestao", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.ln(10)
    for _, row in df.iterrows():
        texto = f"Pedido: {row['numero']} | Cliente: {row['cliente']} | Valor: R$ {row['valor']:.2f}"
        pdf.cell(190, 8, texto.encode('latin-1', 'replace').decode('latin-1'), ln=True)
    return pdf.output(dest='S').encode('latin-1')

def gerar_recibo_pdf(row):
    """Gera um recibo detalhado de uma venda especifica em PDF."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "COMPROVANTE DE VENDA - MD GESTAO", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(190, 8, f"Pedido: {row['numero']}", ln=True)
    pdf.cell(190, 8, f"Cliente: {row['cliente']}", ln=True)
    pdf.cell(190, 8, f"Data: {row['data_criacao']}", ln=True)
    pdf.cell(190, 8, f"Forma de Pagamento: {row['forma_pagamento']}", ln=True)
    
    if row.get('forma_pagamento') == "Fiado / Pendente":
        venc = row.get('data_vencimento', 'Não informada')
        pdf.cell(190, 8, f"Vencimento: {venc}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 8, "Itens Comprados:", ln=True)
    pdf.set_font("Arial", size=10)
    conteudo_itens = str(row['itens_detalhados']) if row['itens_detalhados'] else "Nenhum detalhe registrado"
    pdf.multi_cell(190, 8, conteudo_itens.encode('latin-1', 'replace').decode('latin-1'))
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(190, 10, f"TOTAL A PAGAR: R$ {row['valor']:.2f}", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1')

# --- SISTEMA DE AUTENTICACAO E SEGURANCA ---
def login():
    """Gerencia o bloqueio de tela e cadastro de novos usuarios."""
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.title("🔑 Acesso ao Sistema MD")
        
        # Expander para criacao de conta caso o usuario tenha esquecido ou banco seja novo
        with st.expander("🆕 Criar Novo Perfil de Acesso"):
            st.write("Use esta area para cadastrar voce ou sua mae no sistema.")
            novo_u = st.text_input("Nome de Usuario Desejado", key="reg_user")
            novo_s = st.text_input("Senha de Acesso", type="password", key="reg_pass")
            if st.button("Confirmar Cadastro de Usuario"):
                if novo_u and novo_s:
                    executar_query("INSERT OR IGNORE INTO usuarios (usuario, senha) VALUES (?,?)", (novo_u, novo_s))
                    st.success(f"Usuario '{novo_u}' registrado! Faca login abaixo.")
                else:
                    st.error("Por favor, preencha todos os campos de cadastro.")
        
        st.write("---")
        
        # Formulario principal de entrada
        user = st.text_input("Digite seu Usuario")
        password = st.text_input("Digite sua Senha", type="password")
        
        if st.button("Entrar no Painel"):
            conn = conectar()
            res = conn.execute("SELECT usuario FROM usuarios WHERE usuario=? AND senha=?", (user, password)).fetchone()
            conn.close()
            if res:
                st.session_state.autenticado = True
                st.session_state.user = user
                registrar_log("Login", f"Usuario {user} acessou o sistema")
                st.rerun()
            else: 
                st.error("Usuario ou senha incorretos. Verifique os dados.")
        return False
    return True

# --- INICIO DA INTERFACE LOGADA ---
if login():
    # Barra lateral de navegacao
    st.sidebar.header(f"Sessao ativa: {st.session_state.user}")
    menu = st.sidebar.selectbox("Selecione o modulo:", 
        ["Dashboard", "Vendas", "Perdas", "Financeiro", "Cadastros e Estoque", "Auditoria", "Configuracoes"])
    
    if st.sidebar.button("Encerrar Sessao"):
        registrar_log("Logout", f"Usuario {st.session_state.user} saiu do sistema")
        st.session_state.autenticado = False
        st.rerun()

    # --- 1. MODULO DASHBOARD (VISAO GERAL) ---
    if menu == "Dashboard":
        st.title("📈 Resumo de Performance")
        
        df_est = buscar_dados("estoque")
        df_notas = buscar_dados("notas")
        df_cli = buscar_dados("clientes")
        df_perdas = buscar_dados("perdas")
        
        # Verificacao de estoque baixo para alerta imediato
        if not df_est.empty:
            itens_baixos = df_est[df_est['quantidade'] <= 5]
            if not itens_baixos.empty:
                st.warning(f"Atenção: Voce tem {len(itens_baixos)} itens com estoque critico (menos de 5 unidades)!")
                st.dataframe(itens_baixos[['item', 'quantidade']])

        if not df_cli.empty and not df_notas.empty:
            total_faturado = df_cli['valor_total_devido'].sum()
            total_recebido = df_cli['valor_pago_acumulado'].sum()
            total_prejuizo = df_perdas['custo_total'].sum() if not df_perdas.empty else 0
            
            # Estimativa de lucro baseada em margem de 35%
            lucro_estimado = (total_faturado * 0.35) - total_prejuizo 

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Vendas Totais", f"R$ {total_faturado:.2f}")
            c2.metric("Prejuizo Acumulado", f"R$ {total_prejuizo:.2f}")
            c3.metric("Valor em Caixa", f"R$ {total_recebido:.2f}")
            c4.metric("Lucro Estimado", f"R$ {lucro_estimado:.2f}")

            st.write("---")
            col_g1, col_g2 = st.columns(2)
            
            with col_g1:
                st.subheader("Produtos Mais Vendidos")
                lista_vendas = []
                for item_str in df_notas['itens_detalhados'].dropna():
                    encontrados = re.findall(r'x\s(.*?)(?:,|$)', item_str)
                    lista_vendas.extend(encontrados)
                if lista_vendas:
                    df_pizza = pd.DataFrame(lista_vendas, columns=['Produto']).value_counts().reset_index(name='Qtd')
                    fig = px.pie(df_pizza, values='Qtd', names='Produto', hole=.4)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col_g2:
                st.subheader("Ranking de Clientes (Top 5)")
                top_clientes = df_cli.nlargest(5, 'valor_total_devido')
                st.bar_chart(top_clientes.set_index('nome')['valor_total_devido'])
        else:
            st.info("Ainda nao ha dados suficientes para gerar os graficos de desempenho.")

    # --- 2. MODULO DE VENDAS ---
    elif menu == "Vendas":
        aba_nova, aba_hist = st.tabs(["🛒 Lancar Nova Venda", "📜 Historico de Notas"])
        
        with aba_nova:
            df_cli = buscar_dados("clientes")
            df_est = buscar_dados("estoque")
            
            c_venda, c_carrinho = st.columns([1, 1.2])
            
            with c_venda:
                st.subheader("Dados da Venda")
                cliente_venda = st.selectbox("Selecione o Cliente", df_cli['nome'].tolist() if not df_cli.empty else ["Nenhum Cliente Cadastrado"])
                forma_pagto = st.selectbox("Forma de Pagamento", ["Pix", "Dinheiro", "Debito", "Credito", "Fiado / Pendente"])
                
                vencimento_venda = None
                if forma_pagto == "Fiado / Pendente":
                    vencimento_venda = st.date_input("Data Limite para Pagamento", min_value=datetime.now())
                
                st.write("---")
                st.subheader("Adicionar Produtos")
                if not df_est.empty:
                    lista_itens = [f"{r['id']} - {r['item']} (R$ {r['preco_venda']:.2f})" for _, r in df_est.iterrows()]
                    item_escolhido = st.selectbox("Escolha o Produto", lista_itens)
                    
                    if item_escolhido:
                        id_item = int(item_escolhido.split(" - ")[0])
                        dados_p = df_est[df_est['id'] == id_item].iloc[0]
                        qtd_venda = st.number_input("Quantidade", min_value=1, max_value=int(dados_p['quantidade']))
                        
                        if st.button("Inserir no Carrinho"):
                            st.session_state.carrinho.append({
                                "id": id_item, "item": dados_p['item'], "qtd": qtd_venda,
                                "valor_un": dados_p['preco_venda'], "subtotal": dados_p['preco_venda'] * qtd_venda
                            })
                            st.rerun()
                else:
                    st.error("Nao ha produtos em estoque para vender.")

            with c_carrinho:
                st.subheader("Itens da Venda Atual")
                if st.session_state.carrinho:
                    df_carrinho_atual = pd.DataFrame(st.session_state.carrinho)
                    st.table(df_carrinho_atual[['item', 'qtd', 'subtotal']])
                    valor_final = df_carrinho_atual['subtotal'].sum()
                    
                    if st.button(f"Finalizar e Registrar Venda: R$ {valor_final:.2f}"):
                        data_venda = datetime.now().strftime("%d/%m/%Y %H:%M")
                        str_vencimento = vencimento_venda.strftime("%d/%m/%Y") if vencimento_venda else data_venda
                        detalhes_texto = ", ".join([f"{i['qtd']}x {i['item']}" for i in st.session_state.carrinho])
                        
                        # Salva a nota no banco
                        executar_query(
                            "INSERT INTO notas (cliente, valor, data_criacao, ativo, itens_detalhados, forma_pagamento, data_vencimento) VALUES (?,?,?,1,?,?,?)",
                            (cliente_venda, valor_final, data_venda, detalhes_texto, forma_pagto, str_vencimento)
                        )
                        
                        # Atualiza o financeiro do cliente
                        if forma_pagto == "Fiado / Pendente":
                            executar_query("UPDATE clientes SET valor_total_devido = valor_total_devido + ? WHERE nome = ?", (valor_final, cliente_venda))
                        else:
                            executar_query("UPDATE clientes SET valor_total_devido = valor_total_devido + ?, valor_pago_acumulado = valor_pago_acumulado + ? WHERE nome = ?", (valor_final, valor_final, cliente_venda))
                        
                        # Baixa no estoque
                        for item_c in st.session_state.carrinho:
                            executar_query("UPDATE estoque SET quantidade = quantidade - ? WHERE id = ?", (item_c['qtd'], item_c['id']))
                        
                        registrar_log("Venda", f"Venda de R$ {valor_final} para {cliente_venda}")
                        st.success("Venda registrada com sucesso!")
                        st.session_state.carrinho = []
                        st.rerun()
                    
                    if st.button("Limpar Carrinho"):
                        st.session_state.carrinho = []
                        st.rerun()
                else:
                    st.info("O carrinho esta vazio no momento.")

        with aba_hist:
            st.subheader("Consultar Vendas Realizadas")
            df_vendas_salvas = buscar_dados("notas")
            if not df_vendas_salvas.empty:
                filtro_c = st.text_input("Filtrar por nome de cliente")
                if filtro_c:
                    df_vendas_salvas = df_vendas_salvas[df_vendas_salvas['cliente'].str.contains(filtro_c, case=False)]
                
                for _, n in df_vendas_salvas.sort_values(by='numero', ascending=False).iterrows():
                    with st.expander(f"Cupom #{n['numero']} - {n['cliente']} - Data: {n['data_criacao']}"):
                        st.write(f"**Valor:** R$ {n['valor']:.2f} | **Pagamento:** {n['forma_pagamento']}")
                        st.write(f"**Produtos:** {n['itens_detalhados']}")
                        st.download_button(f"Gerar PDF #{n['numero']}", gerar_recibo_pdf(n), f"Recibo_{n['numero']}.pdf")
            else:
                st.info("Nenhuma venda encontrada no banco de dados.")

    # --- 3. MODULO DE PERDAS ---
    elif menu == "Perdas":
        st.title("📉 Controle de Perdas e Avarias")
        df_est = buscar_dados("estoque")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.subheader("Lancar Novo Prejuizo")
            if not df_est.empty:
                opcoes_perda = [f"{r['id']} - {r['item']}" for _, r in df_est.iterrows()]
                item_perda = st.selectbox("Qual item foi perdido?", opcoes_perda)
                qtd_perdida = st.number_input("Quantidade Perdida", min_value=1)
                motivo_perda = st.text_area("Descreva o motivo (Ex: Vencimento, Quebra)")
                
                if st.button("Registrar Ocorrencia"):
                    id_p = int(item_perda.split(" - ")[0])
                    info_p = df_est[df_est['id'] == id_p].iloc[0]
                    custo_total_perda = info_p['preco_custo'] * qtd_perdida
                    hora_perda = datetime.now().strftime("%d/%m/%Y %H:%M")
                    
                    executar_query(
                        "INSERT INTO perdas (produto_id, item, quantidade, motivo, custo_total, data_hora) VALUES (?,?,?,?,?,?)",
                        (id_p, info_p['item'], qtd_perdida, motivo_perda, custo_total_perda, hora_perda)
                    )
                    executar_query("UPDATE estoque SET quantidade = quantidade - ? WHERE id = ?", (qtd_perdida, id_p))
                    
                    registrar_log("Perda", f"Perda de {qtd_perdida} unidades de {info_p['item']}")
                    st.warning(f"Perda registrada. Prejuizo de R$ {custo_total_perda:.2f}")
                    st.rerun()
            else:
                st.info("Cadastre produtos antes de registrar perdas.")
        
        with col_p2:
            st.subheader("Historico de Prejuizos")
            df_lista_perdas = buscar_dados("perdas")
            if not df_lista_perdas.empty:
                st.dataframe(df_lista_perdas, use_container_width=True)
            else:
                st.info("Nenhuma perda registrada ate agora.")

    # --- 4. MODULO FINANCEIRO ---
    elif menu == "Financeiro":
        st.title("💰 Gestao Financeira e Cobranca")
        df_clientes_fin = buscar_dados("clientes")
        
        # Filtra apenas clientes que possuem dividas
        df_pendentes = df_clientes_fin[df_clientes_fin['valor_total_devido'] > df_clientes_fin['valor_pago_acumulado']] if not df_clientes_fin.empty else pd.DataFrame()
        
        if not df_pendentes.empty:
            st.subheader("Clientes com Pagamentos Pendentes")
            for _, c in df_pendentes.iterrows():
                valor_pendente = c['valor_total_devido'] - c['valor_pago_acumulado']
                with st.expander(f"Devedor: {c['nome']} | Pendencia: R$ {valor_pendente:.2f}"):
                    valor_recebido = st.number_input(f"Valor Pago por {c['nome']}", min_value=0.0, max_value=valor_pendente, key=f"rec_{c['id']}")
                    if st.button("Baixar Pagamento", key=f"btn_{c['id']}"):
                        executar_query("UPDATE clientes SET valor_pago_acumulado = valor_pago_acumulado + ? WHERE id = ?", (valor_recebido, c['id']))
                        registrar_log("Financeiro", f"Recebimento de R$ {valor_recebido} de {c['nome']}")
                        st.success("Pagamento registrado!")
                        st.rerun()
        else:
            st.success("Tudo em dia! Nao ha clientes devendo no momento.")

    # --- 5. MODULO DE CADASTROS E ESTOQUE (INSERINDO CONTROLE DE ESTOQUE) ---
    elif menu == "Cadastros e Estoque":
        aba_prod, aba_cli, aba_estoque = st.tabs(["📦 Cadastro de Produtos", "👥 Cadastro de Clientes", "📥 Entrada de Estoque"])
        
        with aba_prod:
            st.subheader("Registrar Novo Item no Sistema")
            col_in1, col_in2 = st.columns(2)
            with col_in1:
                nome_novo_p = st.text_input("Nome do Produto")
                qtd_inicial = st.number_input("Estoque Inicial", min_value=0)
            with col_in2:
                custo_p = st.number_input("Preco de Compra (Custo)", min_value=0.0)
                venda_p = st.number_input("Preco de Venda", min_value=0.0)
            
            if st.button("Cadastrar Produto"):
                if nome_novo_p:
                    executar_query("INSERT INTO estoque (item, quantidade, preco_custo, preco_venda) VALUES (?,?,?,?)", (nome_novo_p, qtd_inicial, custo_p, venda_p))
                    registrar_log("Cadastro", f"Novo produto: {nome_novo_p}")
                    st.success(f"{nome_novo_p} cadastrado com sucesso!")
                    st.rerun()
            
            st.write("---")
            st.subheader("Estoque Atualizado")
            st.dataframe(buscar_dados("estoque"), use_container_width=True)

        with aba_cli:
            st.subheader("Registrar Novo Cliente")
            c_nome = st.text_input("Nome Completo")
            c_zap = st.text_input("Numero do WhatsApp")
            if st.button("Salvar Cliente"):
                if c_nome:
                    executar_query("INSERT INTO clientes (nome, whatsapp) VALUES (?,?)", (c_nome, c_zap))
                    registrar_log("Cadastro", f"Novo cliente: {c_nome}")
                    st.success("Cliente salvo na base de dados!")
                    st.rerun()
            st.dataframe(buscar_dados("clientes"), use_container_width=True)

        with aba_estoque:
            st.subheader("📥 Entrada de Mercadoria (Reposição)")
            df_repor = buscar_dados("estoque")
            if not df_repor.empty:
                opcoes_repor = [f"{r['id']} - {r['item']}" for _, r in df_repor.iterrows()]
                item_repor = st.selectbox("Selecione o produto que chegou", opcoes_repor)
                qtd_chegou = st.number_input("Quantidade Recebida", min_value=1, key="qtd_repor")
                
                if st.button("Confirmar Entrada de Estoque"):
                    id_repor = int(item_repor.split(" - ")[0])
                    executar_query("UPDATE estoque SET quantidade = quantidade + ? WHERE id = ?", (qtd_chegou, id_repor))
                    registrar_log("Estoque", f"Entrada de {qtd_chegou} unidades para o item ID {id_repor}")
                    st.success("Estoque atualizado com sucesso!")
                    st.rerun()
            else:
                st.info("Nao ha produtos cadastrados para repor.")

    # --- 6. MODULO DE AUDITORIA ---
    elif menu == "Auditoria":
        st.title("🕵️ Auditoria e Logs de Atividade")
        st.write("Aqui voce pode conferir tudo o que foi feito no sistema e por quem.")
        df_logs = buscar_dados("logs")
        if not df_logs.empty:
            st.dataframe(df_logs.sort_values(by='id', ascending=False), use_container_width=True)
        else:
            st.info("Nenhum log registrado.")

    # --- 7. MODULO DE CONFIGURACOES ---
    elif menu == "Configuracoes":
        st.title("⚙️ Configuracoes do Sistema")
        st.subheader("Seguranca e Dados")
        
        from database import DB_PATH
        try:
            with open(DB_PATH, "rb") as f:
                st.download_button("📥 Fazer Backup do Banco de Dados", f, file_name=f"backup_sistema_md_{datetime.now().strftime('%d_%m_%Y')}.db")
        except:
            st.error("Nao foi possivel localizar o arquivo de banco de dados para backup.")
        
        st.write("---")
        st.write("MD Gestao Enterprise - Versao 1.2")