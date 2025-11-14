import { useState, useEffect } from 'react';
import ChatArea from '../components/ChatArea';
import MessageInput from '../components/MessageInput';
import CardapioModal from '../components/CardapioModal';
import { iniciarSessao, enviarMensagem, iniciarPedido } from '../services/api';
import './Home.css';

function Home() {
  const [sessionId, setSessionId] = useState(null);
  const [mensagens, setMensagens] = useState([]);
  const [cardapio, setCardapio] = useState('');
  const [loading, setLoading] = useState(false);
  const [modalAberto, setModalAberto] = useState(false);

  useEffect(() => {
    inicializarSessao();
  }, []);

  const inicializarSessao = async () => {
    try {
      setLoading(true);
      const data = await iniciarSessao();
      setSessionId(data.session_id);
      setCardapio(data.cardapio);
      setMensagens([
        {
          tipo: 'assistant',
          conteudo: data.resposta,
        },
      ]);
    } catch (error) {
      console.error('Erro ao iniciar sessão:', error);
      setMensagens([
        {
          tipo: 'system',
          conteudo: 'Erro ao conectar com o servidor. Por favor, verifique se o backend está rodando.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleEnviarMensagem = async (mensagem) => {
    if (!sessionId) {
      alert('Sessão não iniciada. Por favor, recarregue a página.');
      return;
    }

    // Adiciona mensagem do usuário
    setMensagens((prev) => [
      ...prev,
      {
        tipo: 'user',
        conteudo: mensagem,
      },
    ]);

    setLoading(true);

    try {
      const data = await enviarMensagem(sessionId, mensagem);

      // Adiciona resposta do assistente
      setMensagens((prev) => [
        ...prev,
        {
          tipo: 'assistant',
          conteudo: data.resposta,
        },
      ]);
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      setMensagens((prev) => [
        ...prev,
        {
          tipo: 'system',
          conteudo: 'Ocorreu um erro ao processar sua mensagem. Por favor, tente novamente.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleNovoPedido = async () => {
    if (!sessionId) {
      alert('Sessão não iniciada. Por favor, recarregue a página.');
      return;
    }

    setLoading(true);

    try {
      const data = await iniciarPedido(sessionId);
      setMensagens([
        {
          tipo: 'system',
          conteudo: 'Chat limpo. Você pode iniciar um novo pedido!',
        },
        {
          tipo: 'assistant',
          conteudo: data.resposta,
        },
      ]);
    } catch (error) {
      console.error('Erro ao iniciar pedido:', error);
      setMensagens((prev) => [
        ...prev,
        {
          tipo: 'system',
          conteudo: 'Ocorreu um erro ao iniciar seu pedido. Por favor, tente novamente.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleMostrarCardapio = () => {
    setMensagens((prev) => [
      ...prev,
      {
        tipo: 'system',
        conteudo: cardapio,
      },
    ]);
  };

  const handleLimparChat = () => {
    setMensagens([
      {
        tipo: 'system',
        conteudo: 'Chat limpo. Você pode continuar seu pedido!',
      },
    ]);
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sidebar-header">
          <i className="fas fa-bars"></i>
          <span>Menu</span>
        </div>
        <nav className="sidebar-nav">
          <button className="sidebar-btn" onClick={() => setModalAberto(true)}>
            <i className="fas fa-utensils"></i>
            <span>Ver Cardápio</span>
          </button>
          <a href="/rastreamento" className="sidebar-btn">
            <i className="fas fa-search-location"></i>
            <span>Rastrear Pedido</span>
          </a>
          <a href="/admin" className="sidebar-btn admin-btn">
            <i className="fas fa-shield-alt"></i>
            <span>Admin</span>
          </a>
        </nav>
      </aside>

      <div className="container">
        <header className="header animated">
          <div className="logo">
            <i className="fas fa-pizza-slice"></i>
            <span>Pizzaria</span>
          </div>
          <p className="subheader">O sabor que você merece!</p>
        </header>

        <main>
          <div className="card animated" style={{ animationDelay: '0.1s' }}>
            <div className="card-header">
              <i className="fas fa-comment-alt"></i>
              <span>Faça seu pedido</span>
            </div>
            <div className="card-body">
              <ChatArea mensagens={mensagens} />
              <MessageInput onEnviar={handleEnviarMensagem} loading={loading} />

              <div className="action-buttons">
                <button className="btn" onClick={handleNovoPedido} disabled={loading}>
                  <i className="fas fa-redo-alt"></i>
                  Novo Pedido
                </button>
                <button className="btn btn-secondary" onClick={handleLimparChat}>
                  <i className="fas fa-trash-alt"></i>
                  Limpar Chat
                </button>
              </div>
            </div>
          </div>
        </main>

        <CardapioModal
          isOpen={modalAberto}
          onClose={() => setModalAberto(false)}
          cardapio={cardapio}
        />
      </div>
    </div>
  );
}

export default Home;
