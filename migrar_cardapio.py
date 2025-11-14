"""
Script para migrar dados do cardapioData.js para o banco de dados
Execute uma vez para popular o banco com os itens do cardápio
"""

import database
import database_cardapio

# Inicializar banco (criar tabelas se não existir)
database.init_database()

# Dados do cardápio
cardapio_data = {
    "pizzas_tradicionais": [
        {
            "nome": "Margherita",
            "descricao": "Molho de tomate, mussarela, manjericão",
            "preco": 45.90,
            "imagem": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400&h=300&fit=crop"
        },
        {
            "nome": "Calabresa",
            "descricao": "Molho de tomate, calabresa, cebola",
            "preco": 45.90,
            "imagem": "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=400&h=300&fit=crop"
        },
        {
            "nome": "Portuguesa",
            "descricao": "Presunto, ovo, cebola, azeitona",
            "preco": 45.90,
            "imagem": "https://images.unsplash.com/photo-1594007654729-407eedc4be65?w=400&h=300&fit=crop"
        }
    ],
    "pizzas_especiais": [
        {
            "nome": "Quatro Queijos",
            "descricao": "Mussarela, provolone, parmesão, gorgonzola",
            "preco": 52.90,
            "imagem": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400&h=300&fit=crop"
        },
        {
            "nome": "Frango c/ Catupiry",
            "descricao": "Frango desfiado, catupiry",
            "preco": 52.90,
            "imagem": "https://images.unsplash.com/photo-1571997478779-2adcbbe9ab2f?w=400&h=300&fit=crop"
        },
        {
            "nome": "Pepperoni",
            "descricao": "Molho de tomate, pepperoni, mussarela",
            "preco": 52.90,
            "imagem": "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=400&h=300&fit=crop"
        }
    ],
    "bebidas": [
        {
            "nome": "Refrigerante 2L",
            "descricao": "Coca-Cola, Guaraná, Fanta",
            "preco": 12.90,
            "imagem": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=400&h=300&fit=crop"
        },
        {
            "nome": "Refrigerante Lata",
            "descricao": "350ml - Sabores variados",
            "preco": 6.90,
            "imagem": "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=400&h=300&fit=crop"
        },
        {
            "nome": "Suco Natural",
            "descricao": "Laranja, Limão, Abacaxi",
            "preco": 8.90,
            "imagem": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400&h=300&fit=crop"
        },
        {
            "nome": "Água Mineral",
            "descricao": "500ml gelada",
            "preco": 4.90,
            "imagem": "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=400&h=300&fit=crop"
        }
    ],
    "sobremesas": [
        {
            "nome": "Chocolate com Morango",
            "descricao": "Pizza doce de chocolate com morangos frescos",
            "preco": 39.90,
            "imagem": "https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=400&h=300&fit=crop"
        },
        {
            "nome": "Banana com Canela",
            "descricao": "Pizza doce de banana caramelizada com canela",
            "preco": 37.90,
            "imagem": "https://images.unsplash.com/photo-1571997478779-2adcbbe9ab2f?w=400&h=300&fit=crop"
        },
        {
            "nome": "Doce de Leite com Coco",
            "descricao": "Pizza doce de doce de leite com coco ralado",
            "preco": 39.90,
            "imagem": "https://images.unsplash.com/photo-1593560708920-61dd98c46a4e?w=400&h=300&fit=crop"
        }
    ]
}

# Mapeamento de categorias
categoria_map = {
    "pizzas_tradicionais": "pizza_tradicional",
    "pizzas_especiais": "pizza_especial",
    "bebidas": "bebida",
    "sobremesas": "sobremesa"
}

print("====== MIGRANDO CARDAPIO PARA O BANCO DE DADOS ======\n")

total_inseridos = 0

for categoria_nome, itens in cardapio_data.items():
    categoria_db = categoria_map[categoria_nome]
    print(f"\n[+] Migrando {categoria_nome.replace('_', ' ').title()}...")

    for item in itens:
        try:
            item_id = database_cardapio.adicionar_item_cardapio(
                nome=item['nome'],
                descricao=item['descricao'],
                preco=item['preco'],
                categoria=categoria_db,
                imagem=item['imagem']
            )
            print(f"   [OK] {item['nome']} - R$ {item['preco']:.2f} (ID: {item_id})")
            total_inseridos += 1
        except Exception as e:
            print(f"   [ERRO] Erro ao inserir {item['nome']}: {e}")

print(f"\n====== MIGRACAO CONCLUIDA ======")
print(f"Total de itens inseridos: {total_inseridos}")
print(f"\nCardapio pronto para uso!")
print(f"Acesse o painel admin para gerenciar os itens.\n")
