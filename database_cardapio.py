# Extensão do database.py - Funções de Cardápio
# Importar este módulo juntamente com database.py

from database import get_db_connection

def obter_cardapio_completo():
    """
    Obtém todos os itens do cardápio ativos

    Returns:
        dict: Cardápio organizado por categorias
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, nome, descricao, preco, categoria, imagem
            FROM cardapio
            WHERE ativo = 1
            ORDER BY categoria, nome
        ''')

        # Organizar por categoria
        cardapio = {
            'pizzas_tradicionais': [],
            'pizzas_especiais': [],
            'bebidas': [],
            'sobremesas': []
        }

        categoria_map = {
            'pizza_tradicional': 'pizzas_tradicionais',
            'pizza_especial': 'pizzas_especiais',
            'bebida': 'bebidas',
            'sobremesa': 'sobremesas'
        }

        for row in cursor.fetchall():
            item = {
                'id': row['id'],
                'nome': row['nome'],
                'descricao': row['descricao'],
                'preco': row['preco'],
                'imagem': row['imagem']
            }

            categoria_chave = categoria_map.get(row['categoria'], 'pizzas_tradicionais')
            cardapio[categoria_chave].append(item)

        return cardapio

def obter_itens_cardapio(categoria=None):
    """
    Obtém itens do cardápio, opcionalmente filtrados por categoria

    Args:
        categoria (str): Categoria para filtrar (None = todos)

    Returns:
        list: Lista de itens do cardápio
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        if categoria:
            cursor.execute('''
                SELECT id, nome, descricao, preco, categoria, imagem, ativo
                FROM cardapio
                WHERE categoria = ?
                ORDER BY nome
            ''', (categoria,))
        else:
            cursor.execute('''
                SELECT id, nome, descricao, preco, categoria, imagem, ativo
                FROM cardapio
                ORDER BY categoria, nome
            ''')

        itens = []
        for row in cursor.fetchall():
            itens.append({
                'id': row['id'],
                'nome': row['nome'],
                'descricao': row['descricao'],
                'preco': row['preco'],
                'categoria': row['categoria'],
                'imagem': row['imagem'],
                'ativo': bool(row['ativo'])
            })

        return itens

def adicionar_item_cardapio(nome, descricao, preco, categoria, imagem=None):
    """
    Adiciona um novo item ao cardápio

    Args:
        nome (str): Nome do item
        descricao (str): Descrição do item
        preco (float): Preço do item
        categoria (str): Categoria do item
        imagem (str): URL da imagem (opcional)

    Returns:
        int: ID do item criado
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO cardapio (nome, descricao, preco, categoria, imagem)
            VALUES (?, ?, ?, ?, ?)
        ''', (nome, descricao, preco, categoria, imagem))

        item_id = cursor.lastrowid
        print(f"[OK] Item '{nome}' adicionado ao cardapio")

        return item_id

def atualizar_item_cardapio(item_id, nome=None, descricao=None, preco=None, categoria=None, imagem=None, ativo=None):
    """
    Atualiza um item do cardápio

    Args:
        item_id (int): ID do item
        nome (str): Novo nome (opcional)
        descricao (str): Nova descrição (opcional)
        preco (float): Novo preço (opcional)
        categoria (str): Nova categoria (opcional)
        imagem (str): Nova URL da imagem (opcional)
        ativo (bool): Novo status (opcional)

    Returns:
        bool: True se atualizado com sucesso
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        updates = []
        params = []

        if nome is not None:
            updates.append('nome = ?')
            params.append(nome)

        if descricao is not None:
            updates.append('descricao = ?')
            params.append(descricao)

        if preco is not None:
            updates.append('preco = ?')
            params.append(preco)

        if categoria is not None:
            updates.append('categoria = ?')
            params.append(categoria)

        if imagem is not None:
            updates.append('imagem = ?')
            params.append(imagem)

        if ativo is not None:
            updates.append('ativo = ?')
            params.append(1 if ativo else 0)

        if not updates:
            return False

        params.append(item_id)
        query = f"UPDATE cardapio SET {', '.join(updates)} WHERE id = ?"

        cursor.execute(query, params)
        return cursor.rowcount > 0

def remover_item_cardapio(item_id):
    """
    Remove (desativa) um item do cardápio

    Args:
        item_id (int): ID do item

    Returns:
        bool: True se removido com sucesso
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE cardapio
            SET ativo = 0
            WHERE id = ?
        ''', (item_id,))

        return cursor.rowcount > 0

def deletar_item_cardapio(item_id):
    """
    Deleta permanentemente um item do cardápio

    Args:
        item_id (int): ID do item

    Returns:
        bool: True se deletado com sucesso
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('DELETE FROM cardapio WHERE id = ?', (item_id,))

        return cursor.rowcount > 0
