# 🍕 Pizzaria - Sistema de Pedidos Online

Sistema moderno de chatbot para pedidos de pizzaria desenvolvido com **React + Vite** no frontend e **Flask** no backend.

## ✨ Funcionalidades

- 💬 Chat interativo com atendimento automatizado
- 🎯 Fluxo de pedidos guiado (nome → itens → pagamento → entrega/retirada → endereço)
- 💰 Cálculo automático de valores com detecção inteligente de itens
- 🔄 Suporte a múltiplos usuários simultâneos (sessões isoladas)
- 📊 **Banco de dados SQLite** - Todos os pedidos são salvos automaticamente
- 📈 **API de Consultas** - Endpoints para estatísticas e histórico
- 📱 Interface responsiva e moderna
- 🎨 Animações suaves e UX polida
- 📸 **Cardápio com fotos** - Menu visual com imagens dos produtos em modal interativo

## 🛠️ Tecnologias

### Frontend
- React 18
- Vite
- CSS3 com variáveis customizadas
- Font Awesome
- Google Fonts (Poppins)

### Backend
- Flask
- Flask-CORS
- Google Generative AI (Gemini)
- Python-dotenv
- Unidecode

## 📋 Pré-requisitos

- Python 3.8+
- Node.js 16+
- npm ou yarn

## 🚀 Instalação e Execução

### Opção 1: Scripts Automáticos (Recomendado)

#### Windows:
```batch
# Terminal 1 - Backend
start-backend.bat

# Terminal 2 - Frontend
start-frontend.bat
```

#### Linux/Mac:
```bash
# Inicia ambos (backend + frontend)
./start.sh
```

### Opção 2: Manual

#### 1. Backend (Flask)

```bash
# Instalar dependências Python
pip install -r requirements.txt

# Criar arquivo .env com sua chave do Gemini
copy .env.example .env  # Windows
# ou
cp .env.example .env    # Linux/Mac

# Edite o arquivo .env e adicione sua chave: GEMINI_API_KEY=sua_chave_aqui

# Iniciar servidor Flask
python main.py
```

O backend estará rodando em: `http://localhost:5000`

#### 2. Frontend (React)

```bash
# Entrar na pasta do frontend
cd frontend

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev
```

O frontend estará rodando em: `http://localhost:5173`

## 🔑 Configurando a API Key do Gemini

1. Acesse [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Faça login com sua conta Google
3. Clique em "Get API Key" ou "Create API Key"
4. Copie a chave gerada
5. Adicione a chave no arquivo `.env`:
   ```
   GEMINI_API_KEY=AIza...
   ```

**Nota:** A API do Gemini tem um plano gratuito generoso com 60 requisições por minuto!

## 📊 Banco de Dados

O sistema salva automaticamente todos os pedidos finalizados em um banco SQLite local.

### Endpoints Disponíveis:

- `GET /estatisticas` - Estatísticas gerais (total, ticket médio, etc)
- `GET /pedidos/recentes?limite=10` - Últimos N pedidos
- `GET /pedidos/{id}` - Pedido específico
- `GET /pedidos/cliente/{nome}` - Pedidos de um cliente

**Exemplo:**
```bash
curl http://localhost:5000/estatisticas
curl http://localhost:5000/pedidos/recentes?limite=5
```

📖 **Guia completo:** Veja [DATABASE_GUIDE.md](DATABASE_GUIDE.md) para detalhes sobre consultas SQL, backup e gerenciamento do banco.

## 📸 Cardápio com Fotos

O sistema agora exibe um cardápio visual com imagens dos produtos!

**Características:**
- Grid responsivo com cards de produtos
- Imagens em alta qualidade
- Preços destacados em badges
- Modal interativo acessível pelo header

**Como personalizar as fotos:**
📖 Veja o guia completo em [CUSTOMIZAR_FOTOS.md](CUSTOMIZAR_FOTOS.md)

**Arquivo de dados:**
```
frontend/src/data/cardapioData.js
```

## 📁 Estrutura do Projeto

```
Chatbot/
├── frontend/                    # Aplicação React
│   ├── src/
│   │   ├── components/         # Componentes React
│   │   │   ├── ChatArea.jsx
│   │   │   ├── ChatArea.css
│   │   │   ├── Message.jsx
│   │   │   ├── Message.css
│   │   │   ├── MessageInput.jsx
│   │   │   ├── MessageInput.css
│   │   │   ├── CardapioModal.jsx
│   │   │   ├── CardapioModal.css
│   │   │   ├── CardapioGrid.jsx
│   │   │   ├── CardapioGrid.css
│   │   │   ├── CardapioDisplay.jsx
│   │   │   └── CardapioDisplay.css
│   │   ├── data/               # Dados estruturados
│   │   │   └── cardapioData.js # Cardápio com imagens
│   │   ├── services/           # Serviços de API
│   │   │   └── api.js
│   │   ├── App.jsx             # Componente principal
│   │   ├── App.css
│   │   ├── index.css           # Estilos globais
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── main.py                     # Backend Flask com sessões
├── database.py                 # Módulo de banco de dados
├── pizzaria.db                 # Banco SQLite (auto-gerado)
├── requirements.txt            # Dependências Python
├── .env.example               # Template de configuração
├── .gitignore
├── README.md
├── DATABASE_GUIDE.md           # Guia do banco de dados
├── CUSTOMIZAR_FOTOS.md         # Guia para personalizar imagens do cardápio
├── MIGRATION_GEMINI.md         # Guia de migração para Gemini
├── start-backend.bat          # Script Windows - Backend
├── start-frontend.bat         # Script Windows - Frontend
└── start.sh                   # Script Linux/Mac - Ambos
```

## 🎯 Fluxo de Uso

1. **Usuário acessa a aplicação** → Sistema inicia sessão automática
2. **Nome do cliente** → Sistema solicita o nome
3. **Pedido** → Cliente informa itens desejados (ex: "1 pizza calabresa e 1 coca 2L")
4. **Cálculo** → Sistema identifica itens e calcula valor total
5. **Pagamento** → Cliente escolhe forma de pagamento
6. **Entrega/Retirada** → Cliente define tipo de entrega
7. **Endereço** (se entrega) → Cliente fornece endereço
8. **Confirmação** → Sistema confirma pedido com prazo estimado

## 🔧 Desenvolvimento

### Comandos úteis

**Backend:**
```bash
# Executar em modo debug
python main.py

# Instalar nova dependência
pip install nome-do-pacote
pip freeze > requirements.txt
```

**Frontend:**
```bash
# Build para produção
npm run build

# Preview do build
npm run preview

# Lint
npm run lint
```

## 👨‍💻 Autor

Gabriel Ladoche
