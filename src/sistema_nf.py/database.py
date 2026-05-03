import sqlite3
import os
from datetime import datetime
import pandas as pd

# 1. Definicao de Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "banco.db")

def conectar():
    """Estabelece a conexao com o banco de dados."""
    os.makedirs(DATA_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def executar_query(sql, params=()):
    """Executa comandos SQL (Insert, Update, Delete) e fecha a conexao."""
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
    except Exception as e:
        print(f"Erro ao executar query: {e}")
    finally:
        conn.close()

def buscar_dados(tabela):
    """Retorna um DataFrame de qualquer tabela para o Streamlit."""
    conn = conectar()
    try:
        df = pd.read_sql_query(f"SELECT * FROM {tabela}", conn)
    except Exception as e:
        print(f"Erro ao buscar dados na tabela {tabela}: {e}")
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def registrar_log(evento, detalhes):
    """O fofoqueiro: anota tudo o que acontece no sistema."""
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    executar_query(
        "INSERT INTO logs (data_hora, evento, detalhes) VALUES (?, ?, ?)",
        (data_hora, evento, detalhes)
    )

def criar_tabelas():
    """Cria a estrutura inicial se o banco nao existir."""
    tabelas = {
        "usuarios": "id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT NOT NULL UNIQUE, senha TEXT NOT NULL",
        "notas": """
            numero INTEGER PRIMARY KEY AUTOINCREMENT, 
            cliente TEXT, 
            valor REAL, 
            data_criacao TEXT, 
            ativo INTEGER DEFAULT 1, 
            forma_pagamento TEXT, 
            data_vencimento TEXT, 
            itens_detalhados TEXT
        """,
        "clientes": """
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            nome TEXT NOT NULL UNIQUE, 
            whatsapp TEXT, 
            valor_total_devido REAL DEFAULT 0.0, 
            valor_pago_acumulado REAL DEFAULT 0.0, 
            status_pagamento TEXT DEFAULT 'Regular'
        """,
        "estoque": """
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            item TEXT NOT NULL UNIQUE, 
            quantidade INTEGER DEFAULT 0, 
            preco_custo REAL DEFAULT 0.0, 
            preco_venda REAL DEFAULT 0.0
        """,
        "logs": "id INTEGER PRIMARY KEY AUTOINCREMENT, data_hora TEXT, evento TEXT, detalhes TEXT",
        "perdas": """
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            produto_id INTEGER,
            item TEXT,
            quantidade INTEGER,
            motivo TEXT,
            custo_total REAL,
            data_hora TEXT
        """
    }

    for nome, colunas in tabelas.items():
        executar_query(f"CREATE TABLE IF NOT EXISTS {nome} ({colunas})")
    
    # Executa os ajustes de colunas para garantir compatibilidade
    migration_ajustes()

def migration_ajustes():
    """Garante que as colunas novas existam no banco para as novas funcionalidades."""
    ajustes = [
        ("notas", "forma_pagamento", "TEXT"),
        ("notas", "itens_detalhados", "TEXT"),
        ("notas", "ativo", "INTEGER DEFAULT 1"),
        ("notas", "data_vencimento", "TEXT"),
        ("clientes", "valor_total_devido", "REAL DEFAULT 0.0"),
        ("clientes", "valor_pago_acumulado", "REAL DEFAULT 0.0"),
        ("estoque", "preco_custo", "REAL DEFAULT 0.0"), # <-- ADICIONADO PARA O LUCRO
        ("estoque", "preco_venda", "REAL DEFAULT 0.0")  # <-- GARANTE QUE VENDA EXISTA
    ]
    conn = conectar()
    cursor = conn.cursor()
    for tabela, coluna, tipo in ajustes:
        try:
            cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {tipo}")
        except sqlite3.OperationalError:
            # Se a coluna ja existir, ignoramos o erro
            pass 
    conn.commit()
    conn.close()

if __name__ == "__main__":
    criar_tabelas()
    print(f"Banco de Dados MD sincronizado em: {DB_PATH}")

def criar_usuario_padrao():
    conn = conectar()
    cursor = conn.cursor()
    try:
        # Tenta inserir o admin. Se já existir, ele ignora por causa do UNIQUE
        cursor.execute("INSERT OR IGNORE INTO usuarios (usuario, senha) VALUES (?, ?)", ("admin", "123"))
        conn.commit()
    except Exception as e:
        print(f"Erro ao criar user: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # 1. Garante que as tabelas existam
    criar_tabelas()
    
    # 2. Cria os usuários de emergência
    conn = conectar()
    cursor = conn.cursor()
    
    usuarios_para_criar = [
        ("thainasp", "120723@Tvt"), 
        ("taniamp", "120723@Tvt")
    ]
    
    for u, s in usuarios_para_criar:
        try:
            cursor.execute("INSERT OR IGNORE INTO usuarios (usuario, senha) VALUES (?, ?)", (u, s))
            print(f"✅ Usuário '{u}' pronto para uso!")
        except Exception as e:
            print(f"❌ Erro ao criar '{u}': {e}")
            
    conn.commit()
    conn.close()
    print(f"\n🚀 Banco sincronizado! Agora você já pode logar no Streamlit.")