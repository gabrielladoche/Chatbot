import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import re
import unidecode  # precisa instalar: pip install unidecode
from uuid import uuid4
import google.generativeai as genai
import database  # Módulo de banco de dados
import database_cardapio  # Módulo de cardápio
from difflib import get_close_matches  # Para fuzzy matching

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://localhost:5174"]}})

# Inicializar banco de dados
database.init_database()

# Armazenar sessões de usuários
sessoes = {}

class PizzariaAssistente:
    def __init__(self, session_id=None):
        # Configurar Google Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.session_id = session_id  # Armazenar session_id
        self.pedido_atual = {
            "nome": None,
            "itens": None,
            "pagamento": None,
            "entrega_ou_retirada": None,
            "endereco": None,
            "valor_total": 0,
            "taxa_entrega": 0,
            "status": "iniciando"
        }
        # Buscar preços e cardápio do banco de dados
        self.precos = self._carregar_precos_db()
        self.cardapio = self._gerar_cardapio_db()

    def _carregar_precos_db(self):
        """Carrega preços do banco de dados"""
        try:
            itens = database_cardapio.obter_itens_cardapio()
            precos = {}

            for item in itens:
                if not item['ativo']:
                    continue

                # Criar múltiplas chaves para facilitar busca
                nome_lower = item['nome'].lower()
                precos[nome_lower] = item['preco']

                # Adicionar variações comuns
                if 'c/' in nome_lower:
                    nome_sem_abrev = nome_lower.replace('c/', 'com')
                    precos[nome_sem_abrev] = item['preco']

            return precos
        except Exception as e:
            print(f"[ERRO] Falha ao carregar preços do banco: {e}")
            # Fallback para preços hardcoded em caso de erro
            return {
                "margherita": 45.90,
                "calabresa": 45.90,
                "portuguesa": 45.90,
                "quatro queijos": 52.90,
                "frango com catupiry": 52.90,
                "pepperoni": 52.90,
                "refrigerante 2l": 12.90,
                "refrigerante lata": 6.90,
                "suco natural": 8.90,
                "água mineral": 4.90,
                "chocolate com morango": 39.90,
                "banana com canela": 37.90,
                "doce de leite com coco": 39.90
            }

    def _gerar_cardapio_db(self):
        """Gera cardápio formatado do banco de dados"""
        try:
            cardapio_data = database_cardapio.obter_cardapio_completo()

            cardapio_texto = "CARDAPIO DE PIZZAS\n\n"

            # Pizzas Tradicionais
            if cardapio_data.get('pizzas_tradicionais'):
                cardapio_texto += "PIZZAS TRADICIONAIS\n"
                for item in cardapio_data['pizzas_tradicionais']:
                    cardapio_texto += f"| {item['nome']} ({item['descricao']}) | R$ {item['preco']:.2f}  |\n"
                cardapio_texto += "\n"

            # Pizzas Especiais
            if cardapio_data.get('pizzas_especiais'):
                cardapio_texto += "PIZZAS ESPECIAIS\n"
                for item in cardapio_data['pizzas_especiais']:
                    cardapio_texto += f"| {item['nome']} ({item['descricao']}) | R$ {item['preco']:.2f}  |\n"
                cardapio_texto += "\n"

            # Bebidas
            if cardapio_data.get('bebidas'):
                cardapio_texto += "BEBIDAS\n"
                for item in cardapio_data['bebidas']:
                    cardapio_texto += f"| {item['nome']} | R$ {item['preco']:.2f}  |\n"
                cardapio_texto += "\n"

            # Sobremesas
            if cardapio_data.get('sobremesas'):
                cardapio_texto += "SOBREMESAS (PIZZA DOCE)\n"
                for item in cardapio_data['sobremesas']:
                    cardapio_texto += f"| {item['nome']} ({item['descricao']}) | R$ {item['preco']:.2f}  |\n"
                cardapio_texto += "\n"

            return cardapio_texto
        except Exception as e:
            print(f"[ERRO] Falha ao gerar cardápio do banco: {e}")
            # Fallback para cardápio hardcoded
            return """
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

    def _corrigir_ortografia(self, texto):
        """Corrige erros de ortografia usando fuzzy matching"""
        # Remove acentos e normaliza o texto
        texto_normalizado = unidecode.unidecode(texto.lower())

        # Lista de todos os nomes de itens do cardápio (sem acentos)
        nomes_cardapio = [unidecode.unidecode(nome.lower()) for nome in self.precos.keys()]

        # Divide o texto em palavras
        palavras = texto_normalizado.split()
        texto_corrigido = texto_normalizado
        correcoes = []

        # Para cada palavra, tenta encontrar correspondência no cardápio
        for palavra in palavras:
            if len(palavra) <= 3:  # Ignora palavras muito curtas
                continue

            # Tenta fuzzy match para a palavra
            matches = get_close_matches(palavra, nomes_cardapio, n=1, cutoff=0.7)
            if matches:
                match = matches[0]
                if palavra != match:
                    texto_corrigido = texto_corrigido.replace(palavra, match)
                    correcoes.append((palavra, match))
            else:
                # Tenta fuzzy match para frases compostas (2 palavras)
                if len(palavras) > 1:
                    for i in range(len(palavras) - 1):
                        frase = f"{palavras[i]} {palavras[i+1]}"
                        matches = get_close_matches(frase, nomes_cardapio, n=1, cutoff=0.7)
                        if matches:
                            match = matches[0]
                            if frase != match:
                                texto_corrigido = texto_corrigido.replace(frase, match)
                                correcoes.append((frase, match))

        return texto_corrigido, correcoes

    def calcular_valor_pedido(self, texto_pedido):
        # Primeiro, aplica correção ortográfica
        texto_corrigido, correcoes = self._corrigir_ortografia(texto_pedido)

        # Armazena informações sobre correções para feedback
        self.pedido_atual['correcoes_ortograficas'] = correcoes

        # Continua o processamento com o texto corrigido
        texto_pedido = unidecode.unidecode(texto_corrigido.lower())  # Remove acentos e converte para minúsculas
        valor_total = 0
        itens_encontrados = []

        # Converter números por extenso para dígitos
        numeros_extenso = {
            'uma': '1', 'um': '1', 'dois': '2', 'duas': '2', 'tres': '3', 'quatro': '4',
            'cinco': '5', 'seis': '6', 'sete': '7', 'oito': '8', 'nove': '9', 'dez': '10'
        }
        for extenso, digito in numeros_extenso.items():
            texto_pedido = re.sub(r'\b' + extenso + r'\b', digito, texto_pedido)

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
            "suco": "suco natural", "suco de fruta": "suco natural", "natural": "suco natural",
            "pizza doce": "chocolate com morango", "sobremesa": "chocolate com morango",
            "agua": "agua mineral", "aguinha": "agua mineral",
            "banana": "banana com canela", "pizza de banana": "banana com canela",
            "doce de leite": "doce de leite com coco", "docinho": "doce de leite com coco"
        }

        # Remove palavras auxiliares que atrapalham a detecção, mas mantém espaços
        texto_limpo = re.sub(r'\b(pizza[s]?)\b', '', texto_pedido)

        # Procura por padrões de quantidade + item
        # Padrões: "2 calabresa", "2x margherita", "1 de quatro queijos", "2 portuguesa"
        # Melhorado para capturar itens com múltiplas palavras
        padrao_quantidade = r'(\d+)\s*(?:x|unid\w*|unidades?)?\s*(?:de\s+)?([a-z][a-z\s]+?)(?=\s+e\s+|\s*,|\s*;|\s*\.|$)'
        matches = list(re.finditer(padrao_quantidade, texto_limpo))

        # Debug: print para ver o que está sendo capturado
        print(f"[DEBUG] Texto original: {texto_pedido}")
        print(f"[DEBUG] Texto limpo: {texto_limpo}")
        print(f"[DEBUG] Matches encontrados: {len(matches)}")

        for match in matches:
            qtd = int(match.group(1))
            item_text = match.group(2).strip()

            print(f"[DEBUG] Tentando processar: {qtd}x '{item_text}'")

            # Verifica se o item ou algum sinônimo está no dicionário
            item_encontrado = None

            # Primeiro tenta encontrar correspondência exata
            for item_key in self.precos.keys():
                # Tenta match exato primeiro
                if item_key == item_text:
                    item_encontrado = item_key
                    print(f"[DEBUG] Item encontrado (match exato): {item_key}")
                    break

            # Se não achou match exato, tenta substring
            if not item_encontrado:
                for item_key in self.precos.keys():
                    if item_key in item_text or item_text in item_key:
                        item_encontrado = item_key
                        print(f"[DEBUG] Item encontrado (substring): {item_key}")
                        break

            # Se não encontrou diretamente, tenta pelos sinônimos
            if not item_encontrado:
                for sinonimo, item_real in sinonimos.items():
                    if sinonimo in item_text and item_real in self.precos:
                        item_encontrado = item_real
                        print(f"[DEBUG] Item encontrado via sinônimo '{sinonimo}': {item_real}")
                        break

            if item_encontrado:
                preco = self.precos[item_encontrado]
                valor_total += preco * qtd
                itens_encontrados.append(f"{qtd}x {item_encontrado.title()} (R$ {preco:.2f} cada)")
                print(f"[DEBUG] Adicionado: {qtd}x {item_encontrado} = R$ {preco * qtd:.2f}")

        # Caso o padrão de quantidade não tenha sido encontrado, procura apenas pelos itens
        if not itens_encontrados:
            print("[DEBUG] Nenhum match com quantidade, tentando busca simples...")
            itens_ja_adicionados = set()

            for item, preco in self.precos.items():
                if item in texto_pedido and item not in itens_ja_adicionados:
                    valor_total += preco
                    itens_encontrados.append(f"1x {item.title()} (R$ {preco:.2f})")
                    itens_ja_adicionados.add(item)

            # Tenta identificar pelos sinônimos
            if not itens_encontrados:
                for sinonimo, item_real in sinonimos.items():
                    if sinonimo in texto_pedido and item_real in self.precos and item_real not in itens_ja_adicionados:
                        preco = self.precos[item_real]
                        valor_total += preco
                        itens_encontrados.append(f"1x {item_real.title()} (R$ {preco:.2f})")
                        itens_ja_adicionados.add(item_real)

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

        print(f"[DEBUG] Total de itens encontrados: {len(itens_encontrados)}")
        print(f"[DEBUG] Valor total: R$ {valor_total:.2f}")

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
                # Verifica se o cliente está pedindo para ver o cardápio
                mensagem_lower = mensagem_cliente.lower()
                if any(palavra in mensagem_lower for palavra in ['cardapio', 'cardápio', 'menu', 'opcoes', 'opções', 'tem o que']):
                    resposta_texto = f"Claro! Aqui está nosso cardápio completo:\n\n{self.cardapio}\n\nO que você gostaria de pedir?"
                else:
                    self.pedido_atual["itens"] = mensagem_cliente
                    valor, taxa, itens_encontrados = self.calcular_valor_pedido(mensagem_cliente)
                    self.pedido_atual["valor_total"] = valor

                    if itens_encontrados:
                        texto_itens = "\n".join(itens_encontrados)
                        self.pedido_atual["status"] = "pedindo_pagamento"
                        correcoes = self.pedido_atual.get('correcoes_ortograficas', [])
                        feedback_correcao = ""
                        if correcoes:
                            feedback_correcao = "\n\n(Observação: corrigi automaticamente: "
                            feedback_correcao += ", ".join([f"'{erro}' → '{correto}'" for erro, correto in correcoes])
                            feedback_correcao += ")"
                        resposta_texto = f"Entendi seu pedido:{feedback_correcao}\n\n{texto_itens}\n\nValor total: R$ {valor:.2f}\n\nQual seria a forma de pagamento que você preferiria? Aceitamos cartão de crédito, débito, dinheiro ou Pix."
                    else:
                        correcoes = self.pedido_atual.get('correcoes_ortograficas', [])
                        resposta_texto = "Desculpe, não consegui identificar os itens do seu pedido.\n\n"
                        if correcoes:
                            resposta_texto += "Tentei corrigir algumas palavras, mas ainda não consegui identificar o produto.\n\n"
                        resposta_texto += "Como fazer seu pedido:\n"
                        resposta_texto += "• Use o formato: quantidade + nome do item\n"
                        resposta_texto += "• Exemplos: '1 calabresa', '2 pizzas margherita e 1 coca'\n\n"
                        resposta_texto += "Itens populares:\n"
                        try:
                            itens_db = database_cardapio.obter_itens_cardapio()
                            itens_populares = []
                            for item in itens_db[:6]:
                                if item['ativo']:
                                    itens_populares.append(f"• {item['nome']} - R$ {item['preco']:.2f}")
                            if itens_populares:
                                resposta_texto += "\n".join(itens_populares)
                            else:
                                resposta_texto += "• Calabresa\n• Margherita\n• Portuguesa"
                        except:
                            resposta_texto += "• Calabresa\n• Margherita\n• Portuguesa"
                        resposta_texto += "\n\nDigite 'cardapio' para ver todas as opções!"
                
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
                    self.pedido_atual["taxa_entrega"] = 5.00
                    resposta_texto = f"Valor total com taxa de entrega (R$ 5,00): R$ {valor_total_com_taxa:.2f}\n\nPor favor, forneça seu endereço para que possamos calcular o tempo de entrega."
                else:
                    # Finaliza o pedido para retirada
                    nome = self.pedido_atual["nome"]

                    # Salvar pedido no banco de dados
                    try:
                        pedido_id = database.salvar_pedido(self.session_id, self.pedido_atual)
                        resposta_texto = f"Obrigado, {nome}! Seu pedido #{pedido_id} no valor de R$ {valor_total:.2f} estará pronto para retirada na loja em aproximadamente 30 minutos."
                    except Exception as e:
                        print(f"Erro ao salvar pedido: {e}")
                        resposta_texto = f"Obrigado, {nome}! Seu pedido no valor de R$ {valor_total:.2f} estará pronto para retirada na loja em aproximadamente 30 minutos."

                    # Reseta o pedido
                    self.pedido_atual = {
                        "nome": None,
                        "itens": None,
                        "pagamento": None,
                        "entrega_ou_retirada": None,
                        "endereco": None,
                        "valor_total": 0,
                        "taxa_entrega": 0,
                        "status": "iniciando"
                    }
                
            # Quinto estado - pedir endereço (se for entrega)
            elif self.pedido_atual["status"] == "pedindo_endereco":
                self.pedido_atual["endereco"] = mensagem_cliente
                nome = self.pedido_atual["nome"]
                endereco = mensagem_cliente
                valor_total = self.pedido_atual["valor_total"]

                # Salvar pedido no banco de dados
                try:
                    pedido_id = database.salvar_pedido(self.session_id, self.pedido_atual)
                    resposta_texto = f"Obrigado, {nome}! Seu pedido #{pedido_id} no valor de R$ {valor_total:.2f} será entregue em {endereco} em aproximadamente 45 minutos."
                except Exception as e:
                    print(f"Erro ao salvar pedido: {e}")
                    resposta_texto = f"Obrigado, {nome}! Seu pedido no valor de R$ {valor_total:.2f} será entregue em {endereco} em aproximadamente 45 minutos."

                # Reseta o pedido
                self.pedido_atual = {
                    "nome": None,
                    "itens": None,
                    "pagamento": None,
                    "entrega_ou_retirada": None,
                    "endereco": None,
                    "valor_total": 0,
                    "taxa_entrega": 0,
                    "status": "iniciando"
                }
                
            return resposta_texto
                
        except Exception as e:
            return f"Desculpe, ocorreu um erro: {str(e)}"

    def usar_ia_para_processar(self, prompt):
        try:
            response = self.model.generate_content(prompt)
            return response.text
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

def get_ou_criar_sessao(session_id=None):
    if session_id and session_id in sessoes:
        return sessoes[session_id]

    novo_id = session_id or str(uuid4())
    sessoes[novo_id] = PizzariaAssistente(session_id=novo_id)
    return sessoes[novo_id]

@app.route('/')
def home():
    return jsonify({
        'message': 'API da Pizzaria',
        'status': 'online',
        'frontend': 'http://localhost:5173',
        'endpoints': {
            'iniciar_sessao': 'POST /iniciar_sessao',
            'enviar_mensagem': 'POST /enviar_mensagem',
            'iniciar_pedido': 'POST /iniciar_pedido'
        }
    })

@app.route('/iniciar_sessao', methods=['POST'])
def iniciar_sessao():
    session_id = str(uuid4())
    assistente = get_ou_criar_sessao(session_id)
    return jsonify({
        'session_id': session_id,
        'resposta': 'Bem-vindo! Poderia me dizer seu nome, por favor?',
        'cardapio': assistente.cardapio
    })

@app.route('/enviar_mensagem', methods=['POST'])
def enviar_mensagem():
    data = request.json
    session_id = data.get('session_id')
    mensagem = data.get('mensagem')

    if not session_id:
        return jsonify({'erro': 'Session ID não fornecido'}), 400

    assistente = get_ou_criar_sessao(session_id)
    resposta = assistente.processar_mensagem(mensagem)
    return jsonify({'resposta': resposta})

@app.route('/iniciar_pedido', methods=['POST'])
def iniciar_pedido():
    data = request.json
    session_id = data.get('session_id')

    if not session_id:
        return jsonify({'erro': 'Session ID não fornecido'}), 400

    assistente = get_ou_criar_sessao(session_id)
    assistente.pedido_atual = {
        "nome": None,
        "itens": None,
        "pagamento": None,
        "entrega_ou_retirada": None,
        "endereco": None,
        "valor_total": 0,
        "taxa_entrega": 0,
        "status": "iniciando"
    }
    return jsonify({'resposta': 'Bem-vindo! Poderia me dizer seu nome, por favor?'})

# ========== ENDPOINTS DE CONSULTA DE PEDIDOS ==========

@app.route('/pedidos/recentes', methods=['GET'])
def obter_pedidos_recentes():
    """Retorna os pedidos mais recentes"""
    try:
        limite = request.args.get('limite', 10, type=int)
        pedidos = database.obter_pedidos_recentes(limite)
        return jsonify({
            'sucesso': True,
            'total': len(pedidos),
            'pedidos': pedidos
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/pedidos/<int:pedido_id>', methods=['GET'])
def obter_pedido(pedido_id):
    """Retorna um pedido específico por ID"""
    try:
        pedido = database.obter_pedido_por_id(pedido_id)
        if pedido:
            return jsonify({
                'sucesso': True,
                'pedido': pedido
            })
        else:
            return jsonify({
                'sucesso': False,
                'erro': 'Pedido não encontrado'
            }), 404
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/pedidos/cliente/<nome>', methods=['GET'])
def buscar_pedidos_cliente(nome):
    """Busca pedidos de um cliente por nome"""
    try:
        pedidos = database.buscar_pedidos_por_cliente(nome)
        return jsonify({
            'sucesso': True,
            'total': len(pedidos),
            'pedidos': pedidos
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/estatisticas', methods=['GET'])
def obter_estatisticas():
    """Retorna estatísticas gerais dos pedidos"""
    try:
        stats = database.obter_estatisticas()
        return jsonify({
            'sucesso': True,
            'estatisticas': stats
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/admin/pedidos', methods=['GET'])
def admin_listar_pedidos():
    """Lista todos os pedidos para o admin"""
    try:
        status = request.args.get('status', None)
        pedidos = database.obter_pedidos_por_status(status)
        return jsonify({
            'sucesso': True,
            'total': len(pedidos),
            'pedidos': pedidos
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/admin/pedidos/<int:pedido_id>/status', methods=['PUT'])
def admin_atualizar_status(pedido_id):
    """Atualiza o status de um pedido"""
    try:
        data = request.json
        novo_status = data.get('status')

        if not novo_status:
            return jsonify({
                'sucesso': False,
                'erro': 'Status não fornecido'
            }), 400

        sucesso = database.atualizar_status_pedido(pedido_id, novo_status)

        if sucesso:
            return jsonify({
                'sucesso': True,
                'mensagem': f'Status do pedido #{pedido_id} atualizado para: {novo_status}'
            })
        else:
            return jsonify({
                'sucesso': False,
                'erro': 'Pedido não encontrado'
            }), 404
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

# ====== ENDPOINTS DE CARDÁPIO ======

@app.route('/cardapio', methods=['GET'])
def obter_cardapio():
    """Obtém o cardápio completo organizado por categorias"""
    try:
        cardapio = database_cardapio.obter_cardapio_completo()
        return jsonify({
            'sucesso': True,
            'cardapio': cardapio
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/admin/cardapio', methods=['GET'])
def admin_listar_cardapio():
    """Lista todos os itens do cardápio para gerenciamento"""
    try:
        categoria = request.args.get('categoria', None)
        itens = database_cardapio.obter_itens_cardapio(categoria)

        return jsonify({
            'sucesso': True,
            'total': len(itens),
            'itens': itens
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/admin/cardapio', methods=['POST'])
def admin_adicionar_item():
    """Adiciona um novo item ao cardápio"""
    try:
        data = request.json

        nome = data.get('nome')
        descricao = data.get('descricao')
        preco = data.get('preco')
        categoria = data.get('categoria')
        imagem = data.get('imagem')

        if not all([nome, preco, categoria]):
            return jsonify({
                'sucesso': False,
                'erro': 'Nome, preço e categoria são obrigatórios'
            }), 400

        item_id = database_cardapio.adicionar_item_cardapio(
            nome, descricao, preco, categoria, imagem
        )

        return jsonify({
            'sucesso': True,
            'mensagem': f'Item {nome} adicionado com sucesso',
            'item_id': item_id
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/admin/cardapio/<int:item_id>', methods=['PUT'])
def admin_atualizar_item(item_id):
    """Atualiza um item do cardápio"""
    try:
        data = request.json

        sucesso = database_cardapio.atualizar_item_cardapio(
            item_id,
            nome=data.get('nome'),
            descricao=data.get('descricao'),
            preco=data.get('preco'),
            categoria=data.get('categoria'),
            imagem=data.get('imagem'),
            ativo=data.get('ativo')
        )

        if sucesso:
            return jsonify({
                'sucesso': True,
                'mensagem': f'Item #{item_id} atualizado com sucesso'
            })
        else:
            return jsonify({
                'sucesso': False,
                'erro': 'Item não encontrado'
            }), 404
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/admin/cardapio/<int:item_id>', methods=['DELETE'])
def admin_remover_item(item_id):
    """Remove (desativa) um item do cardápio"""
    try:
        sucesso = database_cardapio.remover_item_cardapio(item_id)

        if sucesso:
            return jsonify({
                'sucesso': True,
                'mensagem': f'Item #{item_id} removido com sucesso'
            })
        else:
            return jsonify({
                'sucesso': False,
                'erro': 'Item não encontrado'
            }), 404
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
