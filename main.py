from openai import OpenAI
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import re
import unidecode  # precisa instalar: pip install unidecode

load_dotenv()

app = Flask(__name__)

class PizzariaAssistente:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        self.pedido_atual = {
            "nome": None,
            "itens": None,
            "pagamento": None,
            "entrega_ou_retirada": None,
            "endereco": None,
            "valor_total": 0,
            "status": "iniciando"
        }
        # Dicionário de preços para cálculo
        self.precos = {
            # Pizzas tradicionais
            "margherita": 45.90,
            "calabresa": 45.90,
            "portuguesa": 45.90,
            # Pizzas especiais
            "quatro queijos": 52.90,
            "frango": 52.90, 
            "catupiry": 52.90,
            "frango com catupiry": 52.90,
            "pepperoni": 52.90,
            # Bebidas
            "refrigerante 2l": 12.90,
            "refrigerante lata": 6.90,
            "suco": 8.90,
            "água": 4.90,
            # Sobremesas
            "chocolate": 39.90,
            "banana": 37.90,
            "doce de leite": 39.90
        }
        self.cardapio = """
💰 CARDÁPIO DE PIZZAS 💰

🍕 PIZZAS TRADICIONAIS
┌─────────────────────────────────────────────────────┬───────────┐
│ Margherita (Molho de tomate, mussarela, manjericão) │ R$ 45,90  │
├─────────────────────────────────────────────────────┼───────────┤
│ Calabresa (Molho de tomate, calabresa, cebola)      │ R$ 45,90  │
├─────────────────────────────────────────────────────┼───────────┤
│ Portuguesa (Presunto, ovo, cebola, azeitona)        │ R$ 45,90  │
└─────────────────────────────────────────────────────┴───────────┘

🍕 PIZZAS ESPECIAIS
┌─────────────────────────────────────────────────────┬───────────┐
│ Quatro Queijos (Mussarela, provolone, parmesão)     │ R$ 52,90  │
├─────────────────────────────────────────────────────┼───────────┤
│ Frango c/ Catupiry (Frango desfiado, catupiry)      │ R$ 52,90  │
├─────────────────────────────────────────────────────┼───────────┤
│ Pepperoni (Molho de tomate, pepperoni, mussarela)   │ R$ 52,90  │
└─────────────────────────────────────────────────────┴───────────┘

🥤 BEBIDAS
┌─────────────────────────────────────────────────────┬───────────┐
│ Refrigerante 2L                                     │ R$ 12,90  │
├─────────────────────────────────────────────────────┼───────────┤
│ Refrigerante Lata                                   │ R$ 6,90   │
├─────────────────────────────────────────────────────┼───────────┤
│ Suco Natural                                        │ R$ 8,90   │
├─────────────────────────────────────────────────────┼───────────┤
│ Água Mineral                                        │ R$ 4,90   │
└─────────────────────────────────────────────────────┴───────────┘

🍫 SOBREMESAS (PIZZA DOCE)
┌─────────────────────────────────────────────────────┬───────────┐
│ Chocolate com Morango                               │ R$ 39,90  │
├─────────────────────────────────────────────────────┼───────────┤
│ Banana com Canela                                   │ R$ 37,90  │
├─────────────────────────────────────────────────────┼───────────┤
│ Doce de Leite com Coco                              │ R$ 39,90  │
└─────────────────────────────────────────────────────┴───────────┘

ℹ️ INFORMAÇÕES
┌─────────────────────────────────────────────────────┬───────────┐
│ Taxa de entrega                                     │ R$ 5,00   │
├─────────────────────────────────────────────────────┼───────────┤
│ Tempo médio de entrega                              │ 45 min    │
└─────────────────────────────────────────────────────┴───────────┘
"""

    def calcular_valor_pedido(self, texto_pedido):
        texto_pedido = unidecode.unidecode(texto_pedido.lower())  # Remove acentos e converte para minúsculas
        valor_total = 0
        itens_encontrados = []
        
        # Sinônimos e termos alternativos para melhorar a detecção
        sinonimos = {
            "coca": "refrigerante 2l", "coca-cola": "refrigerante 2l", "coca cola": "refrigerante 2l",
            "pepsi": "refrigerante 2l", "guarana": "refrigerante 2l", "sprite": "refrigerante 2l",
            "lata": "refrigerante lata", "latinha": "refrigerante lata",
            "pizza de calabresa": "calabresa", "pizza calabresa": "calabresa",
            "portuguesa": "portuguesa", "pizza portuguesa": "portuguesa",
            "4 queijos": "quatro queijos", "pizza 4 queijos": "quatro queijos",
            "frango c/ catupiry": "frango com catupiry", "frango catupiry": "frango com catupiry",
            "pizza de pepperoni": "pepperoni", "peperoni": "pepperoni", "peperrone": "pepperoni",
            "suco": "suco", "suco de fruta": "suco", "natural": "suco",
            "pizza doce": "chocolate", "sobremesa": "chocolate",
            "agua": "água", "aguinha": "água",
            "banana": "banana", "pizza de banana": "banana",
            "doce de leite": "doce de leite", "docinho": "doce de leite"
        }
        
        # Procura por padrões de quantidade + item
        padrao_quantidade = r'(\d+)\s*(?:x|unid\w*|unidades?|pcs)?\s+([\w\s]+?)(?:\.|\,|\;|$|\s+e\s+|\s+com\s+)'
        matches = re.finditer(padrao_quantidade, texto_pedido + ' ')
        
        for match in matches:
            qtd = int(match.group(1))
            item_text = match.group(2).strip()
            
            # Verifica se o item ou algum sinônimo está no dicionário
            item_encontrado = None
            for item_key in self.precos.keys():
                if item_key in item_text:
                    item_encontrado = item_key
                    break
            
            # Se não encontrou diretamente, tenta pelos sinônimos
            if not item_encontrado:
                for sinonimo, item_real in sinonimos.items():
                    if sinonimo in item_text:
                        item_encontrado = item_real
                        break
            
            if item_encontrado:
                preco = self.precos[item_encontrado]
                valor_total += preco * qtd
                itens_encontrados.append(f"{qtd}x {item_encontrado.title()} (R$ {preco:.2f} cada)")
        
        # Caso o padrão de quantidade não tenha sido encontrado, procura apenas pelos itens
        if not itens_encontrados:
            for item, preco in self.precos.items():
                if item in texto_pedido:
                    valor_total += preco
                    itens_encontrados.append(f"1x {item.title()} (R$ {preco:.2f})")
            
            # Tenta identificar pelos sinônimos
            if not itens_encontrados:
                for sinonimo, item_real in sinonimos.items():
                    if sinonimo in texto_pedido and item_real in self.precos:
                        preco = self.precos[item_real]
                        valor_total += preco
                        itens_encontrados.append(f"1x {item_real.title()} (R$ {preco:.2f})")
        
        # Se ainda não identificou nada, procura por palavras-chave gerais
        if not itens_encontrados:
            if "pizza" in texto_pedido:
                # Assume uma pizza tradicional se mencionou pizza
                valor_total += 45.90
                itens_encontrados.append("1x Pizza Tradicional (R$ 45.90)")
            
            if "refri" in texto_pedido:
                valor_total += 12.90
                itens_encontrados.append("1x Refrigerante 2L (R$ 12.90)")
        
        taxa_entrega = 0
        
        return valor_total, taxa_entrega, itens_encontrados

    def processar_mensagem(self, mensagem_cliente):
        try:
            # Estado inicial - pedir nome
            if self.pedido_atual["status"] == "iniciando":
                self.pedido_atual["nome"] = mensagem_cliente
                self.pedido_atual["status"] = "pedindo_itens"
                resposta_texto = f"Muito obrigado, {mensagem_cliente}! Qual seria o seu pedido hoje?"
                
            # Segundo estado - pedir itens
            elif self.pedido_atual["status"] == "pedindo_itens":
                self.pedido_atual["itens"] = mensagem_cliente
                
                # Calcular valor do pedido
                valor, taxa, itens_encontrados = self.calcular_valor_pedido(mensagem_cliente)
                self.pedido_atual["valor_total"] = valor
                
                # Formatar resposta com itens e valor
                if itens_encontrados:
                    texto_itens = "\n".join(itens_encontrados)
                    self.pedido_atual["status"] = "pedindo_pagamento"
                    resposta_texto = f"Entendi seu pedido:\n\n{texto_itens}\n\nValor total: R$ {valor:.2f}\n\nQual seria a forma de pagamento que você preferiria? Aceitamos cartão de crédito, débito, dinheiro ou Pix."
                else:
                    # Se não conseguiu identificar, pede confirmação manual
                    resposta_texto = "Desculpe, não consegui identificar os itens do seu pedido. Poderia por favor informar novamente com o formato: quantidade + item? Por exemplo: '1 pizza de calabresa e 1 refrigerante 2L'"
                    # Mantém no mesmo estado para tentar novamente
                
            # Terceiro estado - pedir forma de pagamento
            elif self.pedido_atual["status"] == "pedindo_pagamento":
                self.pedido_atual["pagamento"] = mensagem_cliente
                self.pedido_atual["status"] = "pedindo_entrega_ou_retirada"
                resposta_texto = "Seria para entrega ou você gostaria de retirar seu pedido na loja?"
                
            # Quarto estado - perguntar sobre entrega ou retirada
            elif self.pedido_atual["status"] == "pedindo_entrega_ou_retirada":
                self.pedido_atual["entrega_ou_retirada"] = mensagem_cliente
                valor_total = self.pedido_atual["valor_total"]
                
                if "entrega" in mensagem_cliente.lower():
                    self.pedido_atual["status"] = "pedindo_endereco"
                    # Adiciona taxa de entrega
                    valor_total_com_taxa = valor_total + 5.00
                    self.pedido_atual["valor_total"] = valor_total_com_taxa
                    resposta_texto = f"Valor total com taxa de entrega (R$ 5,00): R$ {valor_total_com_taxa:.2f}\n\nPor favor, forneça seu endereço para que possamos calcular o tempo de entrega."
                else:
                    # Finaliza o pedido para retirada
                    nome = self.pedido_atual["nome"]
                    resposta_texto = f"Obrigado, {nome}! Seu pedido no valor de R$ {valor_total:.2f} estará pronto para retirada na loja em aproximadamente 30 minutos."
                    # Reseta o pedido
                    self.pedido_atual = {
                        "nome": None,
                        "itens": None,
                        "pagamento": None,
                        "entrega_ou_retirada": None,
                        "endereco": None,
                        "valor_total": 0,
                        "status": "iniciando"
                    }
                
            # Quinto estado - pedir endereço (se for entrega)
            elif self.pedido_atual["status"] == "pedindo_endereco":
                self.pedido_atual["endereco"] = mensagem_cliente
                nome = self.pedido_atual["nome"]
                endereco = mensagem_cliente
                valor_total = self.pedido_atual["valor_total"]
                resposta_texto = f"Obrigado, {nome}! Seu pedido no valor de R$ {valor_total:.2f} será entregue em {endereco} em aproximadamente 45 minutos."
                
                # Reseta o pedido
                self.pedido_atual = {
                    "nome": None,
                    "itens": None,
                    "pagamento": None,
                    "entrega_ou_retirada": None,
                    "endereco": None,
                    "valor_total": 0,
                    "status": "iniciando"
                }
                
            return resposta_texto
                
        except Exception as e:
            return f"Desculpe, ocorreu um erro: {str(e)}"

    def usar_ia_para_processar(self, prompt):
        try:
            completion = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "http://localhost:5000", 
                    "X-Title": "Pizzaria Virtual",
                },
                model="deepseek/deepseek-r1-zero:free",
    messages=[
        {
            "role": "user",
                        "content": prompt
                    }
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Erro ao processar com IA: {str(e)}"

    def iniciar_atendimento(self):
        print("\n=== 🍕 Bem-vindo à Pizzaria Virtual! 🍕 ===")
        print("Digite 'cardapio' para ver as opções")
        print("Digite 'finalizar' para concluir seu pedido")
        print("Digite 'sair' para encerrar o atendimento\n")
        
        nome_cliente = input("Por favor, digite seu nome: ")
        print(f"\nOlá {nome_cliente}! Como posso ajudar você hoje? 😊")
        
        while True:
            mensagem = input("\nVocê: ")
            
            if mensagem.lower() == 'sair':
                print("\nObrigado pela preferência! Volte sempre! 👋")
                break
                
            if mensagem.lower() == 'cardapio':
                print(self.cardapio)
                continue
                
            print("\nAtendente:", end=" ")
            self.processar_mensagem(mensagem)

assistente = PizzariaAssistente()

@app.route('/')
def home():
    return render_template('index.html', cardapio=assistente.cardapio)

@app.route('/enviar_mensagem', methods=['POST'])
def enviar_mensagem():
    mensagem = request.json['mensagem']
    resposta = assistente.processar_mensagem(mensagem)
    return jsonify({'resposta': resposta})

@app.route('/iniciar_pedido', methods=['GET'])
def iniciar_pedido():
    assistente.pedido_atual = {
        "nome": None,
        "itens": None,
        "pagamento": None,
        "entrega_ou_retirada": None,
        "endereco": None,
        "valor_total": 0,
        "status": "iniciando"
    }
    return jsonify({'resposta': 'Bem-vindo! Poderia me dizer seu nome, por favor?'})

if __name__ == '__main__':
    app.run(debug=True)
