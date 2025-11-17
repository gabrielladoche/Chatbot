# 🍕 Pizzaria Chatbot - Sistema de Pedidos Inteligente

<div align="center">

![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Google AI](https://img.shields.io/badge/Gemini_AI-4285F4?style=for-the-badge&logo=google&logoColor=white)

Sistema moderno de atendimento automatizado para pedidos de pizzaria, desenvolvido com **React + Vite** no frontend e **Flask** no backend, integrado com **Google Gemini AI**.

[Demo](#) • [Documentação](#-documentação) • [Instalação](#-instalação-rápida)

</div>

---

## 📖 Sobre o Projeto

Aplicação full-stack que simula um sistema real de pedidos para pizzaria, com chatbot inteligente que guia o cliente através de todo o processo de compra - desde a escolha dos produtos até a confirmação da entrega.

### 🎯 Objetivos

- Demonstrar integração frontend + backend + IA
- Implementar gerenciamento de estado e sessões
- Aplicar boas práticas de desenvolvimento web
- Criar interface responsiva e intuitiva

---

## ✨ Funcionalidades

### 💬 Chat Inteligente
- Atendimento automatizado com IA (Google Gemini)
- Compreensão natural de linguagem
- Suporte a múltiplos usuários simultâneos com sessões isoladas

### 📊 Gestão de Pedidos
- Cálculo automático de valores
- Identificação inteligente de produtos
- Banco de dados SQLite integrado
- API RESTful para consultas e estatísticas

### 🎨 Interface Moderna
- Design responsivo e mobile-first
- Cardápio visual com imagens em modal interativo
- Animações suaves e feedback visual
- Tema customizável com CSS variables

### 📈 Funcionalidades Técnicas
- Sistema de sessões por usuário
- Validação de dados em tempo real
- Tratamento de erros robusto
- Logs detalhados para debugging

---

## 🛠️ Tecnologias Utilizadas

### Frontend
```
React 18         • Biblioteca UI
Vite            • Build tool e dev server
CSS3            • Estilização moderna
Font Awesome    • Ícones
```

### Backend
```
Flask           • Framework web Python
Google Gemini   • Inteligência artificial
SQLite          • Banco de dados
Flask-CORS      • Gerenciamento de CORS
```

---

## 🚀 Instalação Rápida

### Pré-requisitos
- Python 3.8+
- Node.js 16+
- Chave API do Google Gemini ([obter aqui](https://makersuite.google.com/app/apikey))

### 1️⃣ Clone o repositório
```bash
git clone https://github.com/gabrielladoche/Chatbot.git
cd Chatbot
```

### 2️⃣ Configure o Backend
```bash
# Instale as dependências
pip install -r requirements.txt

# Configure a chave da API
cp .env.example .env
# Edite o arquivo .env e adicione sua GEMINI_API_KEY
```

### 3️⃣ Configure o Frontend
```bash
cd frontend
npm install
```

### 4️⃣ Execute a aplicação

**Opção 1 - Scripts automatizados:**
```bash
# Windows
start-backend.bat   # Terminal 1
start-frontend.bat  # Terminal 2

# Linux/Mac
./start.sh
```

**Opção 2 - Manual:**
```bash
# Terminal 1 - Backend
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Acesse: **http://localhost:5173**

---

## 📊 API Endpoints

### Consultas de Pedidos
```bash
GET /estatisticas              # Estatísticas gerais
GET /pedidos/recentes?limite=N # Últimos N pedidos
GET /pedidos/{id}             # Pedido específico
GET /pedidos/cliente/{nome}   # Pedidos por cliente
```

### Exemplo de resposta
```json
{
  "total_pedidos": 150,
  "ticket_medio": 45.80,
  "item_mais_vendido": "Pizza Margherita",
  "receita_total": 6870.00
}
```

---

## 🎨 Personalização

### Cardápio com Fotos
```javascript
// frontend/src/data/cardapioData.js
export const pizzas = [
  {
    nome: "Margherita",
    preco: 35.00,
    imagem: "URL_DA_IMAGEM"
  }
]
```



---

## 📁 Estrutura do Projeto
```
Chatbot/
├── frontend/                  # React App
│   ├── src/
│   │   ├── components/       # Componentes reutilizáveis
│   │   ├── data/            # Dados estáticos
│   │   └── services/        # Integrações API
│   └── package.json
│
├── main.py                   # Backend Flask
├── database.py              # Módulo SQLite
├── pizzaria.db             # Banco de dados
└── requirements.txt        # Dependências Python
```

---

## 🔄 Fluxo de Atendimento
```
1. Cliente acessa → Sistema cria sessão única
2. Solicita nome → Armazena identificação
3. Cliente pede → "1 pizza calabresa e 1 coca 2L"
4. IA identifica → Calcula valor automático
5. Escolhe pagamento → Dinheiro/Cartão/PIX
6. Define entrega → Delivery ou Retirada
7. Informa endereço → (se delivery)
8. Confirma pedido → Salvo no banco + prazo estimado
```

---

## 🎯 Aprendizados e Desafios

### Desafios Técnicos Superados
✅ Integração de IA com processamento de linguagem natural  
✅ Gerenciamento de múltiplas sessões simultâneas  
✅ Cálculo dinâmico de preços com regex patterns  
✅ Arquitetura escalável frontend + backend  

### Conceitos Aplicados
- REST API design
- State management (React)
- Session handling (Flask)
- Database modeling (SQLite)
- AI prompt engineering
- Responsive design

---

## 👨‍💻 Desenvolvedor

**Gabriel Ladoche**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/gabriel-ladoche-5a3aba222/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/gabrielladoche)


---



</div>
