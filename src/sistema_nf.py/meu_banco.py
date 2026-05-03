import sqlite3

class MDGestao_Engine:
    def __init__(self):
        # Conexão com o banco oficial do projeto
        self.conn = sqlite3.connect('md_gestao_v1.db')
        self.cursor = self.conn.cursor()
        self.setup_professional_schema()

    def setup_professional_schema(self):
        """Cria a estrutura base para Gestão, BI e Futuro ML"""
        # 1. Cadastro Unificado de Clientes (Fase 2)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                contato TEXT,
                ticket_medio REAL DEFAULT 0.0
            )
        ''')

        # 2. Gestão de Estoque e Insumos (Fase 2)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS estoque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                quantidade INTEGER DEFAULT 0,
                preco_custo REAL
            )
        ''')

        # 3. Registro de Pedidos (O fluxo de Notas que você iniciou)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER,
                descricao_servico TEXT NOT NULL,
                valor_venda REAL NOT NULL,
                data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'PENDENTE',
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            )
        ''')
        self.conn.commit()

    # Métodos de inserção e consulta viriam aqui...