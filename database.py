import sqlite3
from datetime import datetime
import json
from contextlib import contextmanager

DATABASE_NAME = 'pizzaria.db'

@contextmanager
def get_db_connection():
    """Context manager para conexão com o banco de dados"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_database():
    """Inicializa o banco de dados com as tabelas necessárias"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Tabela de pedidos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                nome_cliente TEXT NOT NULL,
                itens TEXT NOT NULL,
                valor_total REAL NOT NULL,
                taxa_entrega REAL DEFAULT 0,
                forma_pagamento TEXT,
                tipo_entrega TEXT,
                endereco TEXT,
                status TEXT DEFAULT 'finalizado',
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                observacoes TEXT
            )
        ''')

        # Tabela de itens do pedido (normalizado)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS itens_pedido (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER NOT NULL,
                nome_item TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                preco_unitario REAL NOT NULL,
                preco_total REAL NOT NULL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos (id)
            )
        ''')

        # Tabela de cardápio
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cardapio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                preco REAL NOT NULL,
                categoria TEXT NOT NULL,
                imagem TEXT,
                ativo BOOLEAN DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Índices para melhorar performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_pedidos_session
            ON pedidos(session_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_pedidos_data
            ON pedidos(data_criacao)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cardapio_categoria
            ON cardapio(categoria)
        ''')

        print("[OK] Banco de dados inicializado com sucesso!")

def salvar_pedido(session_id, pedido_data):
    """
    Salva um pedido no banco de dados

    Args:
        session_id (str): ID da sessão
        pedido_data (dict): Dados do pedido com as chaves:
            - nome: nome do cliente
            - itens: descrição dos itens
            - valor_total: valor total do pedido
            - taxa_entrega: taxa de entrega (opcional)
            - pagamento: forma de pagamento
            - entrega_ou_retirada: tipo de entrega
            - endereco: endereço (se entrega)

    Returns:
        int: ID do pedido salvo
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO pedidos (
                session_id, nome_cliente, itens, valor_total,
                taxa_entrega, forma_pagamento, tipo_entrega, endereco
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            pedido_data.get('nome'),
            pedido_data.get('itens'),
            pedido_data.get('valor_total', 0),
            pedido_data.get('taxa_entrega', 0),
            pedido_data.get('pagamento'),
            pedido_data.get('entrega_ou_retirada'),
            pedido_data.get('endereco')
        ))

        pedido_id = cursor.lastrowid
        print(f"[OK] Pedido #{pedido_id} salvo para {pedido_data.get('nome')}")

        return pedido_id

def obter_pedidos_recentes(limite=10):
    """
    Obtém os pedidos mais recentes

    Args:
        limite (int): Número máximo de pedidos a retornar

    Returns:
        list: Lista de dicionários com os pedidos
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                id, session_id, nome_cliente, itens, valor_total,
                taxa_entrega, forma_pagamento, tipo_entrega, endereco,
                status, data_criacao
            FROM pedidos
            ORDER BY data_criacao DESC
            LIMIT ?
        ''', (limite,))

        pedidos = []
        for row in cursor.fetchall():
            pedidos.append({
                'id': row['id'],
                'session_id': row['session_id'],
                'nome_cliente': row['nome_cliente'],
                'itens': row['itens'],
                'valor_total': row['valor_total'],
                'taxa_entrega': row['taxa_entrega'],
                'forma_pagamento': row['forma_pagamento'],
                'tipo_entrega': row['tipo_entrega'],
                'endereco': row['endereco'],
                'status': row['status'],
                'data_criacao': row['data_criacao']
            })

        return pedidos

def obter_pedido_por_id(pedido_id):
    """
    Obtém um pedido específico por ID

    Args:
        pedido_id (int): ID do pedido

    Returns:
        dict: Dados do pedido ou None se não encontrado
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                id, session_id, nome_cliente, itens, valor_total,
                taxa_entrega, forma_pagamento, tipo_entrega, endereco,
                status, data_criacao
            FROM pedidos
            WHERE id = ?
        ''', (pedido_id,))

        row = cursor.fetchone()
        if row:
            return {
                'id': row['id'],
                'session_id': row['session_id'],
                'nome_cliente': row['nome_cliente'],
                'itens': row['itens'],
                'valor_total': row['valor_total'],
                'taxa_entrega': row['taxa_entrega'],
                'forma_pagamento': row['forma_pagamento'],
                'tipo_entrega': row['tipo_entrega'],
                'endereco': row['endereco'],
                'status': row['status'],
                'data_criacao': row['data_criacao']
            }
        return None

def obter_estatisticas():
    """
    Obtém estatísticas gerais dos pedidos

    Returns:
        dict: Estatísticas do sistema
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Total de pedidos
        cursor.execute('SELECT COUNT(*) as total FROM pedidos')
        total_pedidos = cursor.fetchone()['total']

        # Valor total vendido
        cursor.execute('SELECT SUM(valor_total) as total FROM pedidos')
        valor_total = cursor.fetchone()['total'] or 0

        # Pedidos de hoje
        cursor.execute('''
            SELECT COUNT(*) as total
            FROM pedidos
            WHERE DATE(data_criacao) = DATE('now')
        ''')
        pedidos_hoje = cursor.fetchone()['total']

        # Ticket médio
        ticket_medio = valor_total / total_pedidos if total_pedidos > 0 else 0

        return {
            'total_pedidos': total_pedidos,
            'valor_total': round(valor_total, 2),
            'pedidos_hoje': pedidos_hoje,
            'ticket_medio': round(ticket_medio, 2)
        }

def buscar_pedidos_por_cliente(nome_cliente):
    """
    Busca pedidos de um cliente específico

    Args:
        nome_cliente (str): Nome do cliente

    Returns:
        list: Lista de pedidos do cliente
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                id, session_id, nome_cliente, itens, valor_total,
                taxa_entrega, forma_pagamento, tipo_entrega, endereco,
                status, data_criacao
            FROM pedidos
            WHERE nome_cliente LIKE ?
            ORDER BY data_criacao DESC
        ''', (f'%{nome_cliente}%',))

        pedidos = []
        for row in cursor.fetchall():
            pedidos.append({
                'id': row['id'],
                'session_id': row['session_id'],
                'nome_cliente': row['nome_cliente'],
                'itens': row['itens'],
                'valor_total': row['valor_total'],
                'taxa_entrega': row['taxa_entrega'],
                'forma_pagamento': row['forma_pagamento'],
                'tipo_entrega': row['tipo_entrega'],
                'endereco': row['endereco'],
                'status': row['status'],
                'data_criacao': row['data_criacao']
            })

        return pedidos

def atualizar_status_pedido(pedido_id, novo_status):
    """
    Atualiza o status de um pedido

    Args:
        pedido_id (int): ID do pedido
        novo_status (str): Novo status do pedido

    Returns:
        bool: True se atualizado com sucesso
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE pedidos
            SET status = ?
            WHERE id = ?
        ''', (novo_status, pedido_id))

        return cursor.rowcount > 0

def obter_pedidos_por_status(status=None):
    """
    Obtém pedidos filtrados por status

    Args:
        status (str): Status para filtrar (None = todos)

    Returns:
        list: Lista de pedidos
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        if status:
            cursor.execute('''
                SELECT
                    id, session_id, nome_cliente, itens, valor_total,
                    taxa_entrega, forma_pagamento, tipo_entrega, endereco,
                    status, data_criacao
                FROM pedidos
                WHERE status = ?
                ORDER BY data_criacao DESC
            ''', (status,))
        else:
            cursor.execute('''
                SELECT
                    id, session_id, nome_cliente, itens, valor_total,
                    taxa_entrega, forma_pagamento, tipo_entrega, endereco,
                    status, data_criacao
                FROM pedidos
                ORDER BY data_criacao DESC
            ''')

        pedidos = []
        for row in cursor.fetchall():
            pedidos.append({
                'id': row['id'],
                'session_id': row['session_id'],
                'nome_cliente': row['nome_cliente'],
                'itens': row['itens'],
                'valor_total': row['valor_total'],
                'taxa_entrega': row['taxa_entrega'],
                'forma_pagamento': row['forma_pagamento'],
                'tipo_entrega': row['tipo_entrega'],
                'endereco': row['endereco'],
                'status': row['status'],
                'data_criacao': row['data_criacao']
            })

        return pedidos
