from groq import Groq
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from datetime import datetime

load_dotenv()

app = Flask(__name__)

class PizzariaAssistente:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.pedido_atual = {
            "itens": None,
            "endereco": None,
            "total": 0
        }
        self.cardapio = """
🍕 CARDÁPIO DE PIZZAS:
Tradicionais (R$ 45,90):
- Margherita: Molho de tomate, mussarela, manjericão fresco
- Calabresa: Molho de tomate, calabresa, cebola
- Portuguesa: Molho de tomate, presunto, ovo, cebola, azeitona

Especiais (R$ 52,90):
- Quatro Queijos: Mussarela, provolone, parmesão, gorgonzola
- Frango com Catupiry: Frango desfiado, catupiry, milho
- Pepperoni: Molho de tomate, pepperoni, mussarela

🥤 BEBIDAS:
- Refrigerante 2L: R$ 12,90
- Refrigerante Lata: R$ 6,90
- Suco Natural: R$ 8,90
- Água Mineral: R$ 4,90

🍫 SOBREMESAS (Pizza Doce):
- Chocolate com Morango: R$ 39,90
- Banana com Canela: R$ 37,90
- Doce de Leite com Coco: R$ 39,90

ℹ️ Informações:
- Taxa de entrega: R$ 5,00
- Tempo médio de entrega: 45 minutos"""

    def processar_mensagem(self, mensagem_cliente):
        try:
            if not self.pedido_atual["itens"]:
                # Primeira mensagem: Verifica se é delivery ou retirada
                if "retirada" in mensagem_cliente.lower():
                    completion = self.client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {
                                "role": "system",
                                "content": """Confirme o pedido para retirada:
                                1. Confirme os itens e valor total
                                2. Informe que estará pronto em 30 minutos
                                3. Agradeça o pedido
                                4. Seja conciso"""
                            },
                            {
                                "role": "user",
                                "content": mensagem_cliente
                            }
                        ],
                        temperature=0.7,
                        max_completion_tokens=1024,
                        stream=True
                    )
                    # Reseta o pedido após finalizar
                    self.pedido_atual = {"itens": None, "endereco": None, "total": 0}
                else:
                    # Se não for retirada, assume delivery e pede endereço
                    completion = self.client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {
                                "role": "system",
                                "content": """Confirme o pedido e peça o endereço:
                                1. Confirme os itens e valores
                                2. Peça o endereço de entrega
                                3. Seja conciso"""
                            },
                            {
                                "role": "user",
                                "content": mensagem_cliente
                            }
                        ],
                        temperature=0.7,
                        max_completion_tokens=1024,
                        stream=True
                    )
                    self.pedido_atual["itens"] = mensagem_cliente
            
            elif not self.pedido_atual["endereco"]:
                # Segunda mensagem: Apenas para delivery - finaliza com endereço
                self.pedido_atual["endereco"] = mensagem_cliente
                completion = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": """Finalize o pedido:
                            1. Confirme o endereço
                            2. Informe taxa de entrega (R$ 5,00) e valor total
                            3. Informe tempo de entrega (45 minutos)
                            4. Agradeça o pedido
                            5. Seja conciso"""
                        },
                        {
                            "role": "user",
                            "content": f"Endereço: {mensagem_cliente}"
                        }
                    ],
                    temperature=0.7,
                    max_completion_tokens=1024,
                    stream=True
                )
                # Reseta o pedido após finalizar
                self.pedido_atual = {"itens": None, "endereco": None, "total": 0}
            
            resposta_completa = ""
            for chunk in completion:
                pedaco_resposta = chunk.choices[0].delta.content or ""
                resposta_completa += pedaco_resposta
                print(pedaco_resposta, end="", flush=True)
            print("\n")
            return resposta_completa
            
        except Exception as e:
            return f"Desculpe, ocorreu um erro: {str(e)}"

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

if __name__ == '__main__':
    app.run(debug=True)
