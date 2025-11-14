import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import './Rastreamento.css';

const API_URL = 'http://localhost:5000';

const STATUS_TIMELINE = [
  { key: 'finalizado', label: 'Pedido Finalizado', icon: 'check-circle' },
  { key: 'confirmado', label: 'Confirmado', icon: 'clipboard-check' },
  { key: 'preparando', label: 'Preparando', icon: 'fire' },
  { key: 'pronto', label: 'Pronto', icon: 'check' },
  { key: 'saiu_entrega', label: 'Saiu para Entrega', icon: 'truck' },
  { key: 'entregue', label: 'Entregue', icon: 'home' }
];

const Rastreamento = () => {
  const [searchParams] = useSearchParams();
  const [pedidoId, setPedidoId] = useState(searchParams.get('id') || '');
  const [pedido, setPedido] = useState(null);
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState(null);

  useEffect(() => {
    if (searchParams.get('id')) {
      buscarPedido(searchParams.get('id'));
    }
  }, [searchParams]);

  useEffect(() => {
    // Atualizar automaticamente a cada 15 segundos se houver pedido
    if (!pedido) return;

    const interval = setInterval(() => {
      buscarPedido(pedido.id, true);
    }, 15000);

    return () => clearInterval(interval);
  }, [pedido]);

  const buscarPedido = async (id, silencioso = false) => {
    if (!id) {
      setErro('Por favor, informe o número do pedido');
      return;
    }

    try {
      if (!silencioso) {
        setLoading(true);
        setErro(null);
        setPedido(null);
      }

      const response = await fetch(`${API_URL}/pedidos/${id}`);
      const data = await response.json();

      if (data.sucesso) {
        setPedido(data.pedido);
      } else {
        setErro('Pedido não encontrado');
        setPedido(null);
      }
    } catch (error) {
      console.error('Erro ao buscar pedido:', error);
      setErro('Erro ao buscar pedido. Verifique sua conexão.');
    } finally {
      if (!silencioso) {
        setLoading(false);
      }
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    buscarPedido(pedidoId);
  };

  const getCurrentStepIndex = (status) => {
    return STATUS_TIMELINE.findIndex(s => s.key === status);
  };

  const formatarData = (dataString) => {
    const data = new Date(dataString);
    return data.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getTempoEstimado = (pedido) => {
    if (!pedido) return '';

    const agora = new Date();
    const criacao = new Date(pedido.data_criacao);
    const diff = Math.floor((agora - criacao) / 60000); // minutos

    if (pedido.status === 'entregue') {
      return 'Pedido já foi entregue!';
    }

    if (pedido.tipo_entrega === 'entrega') {
      const tempoTotal = 45; // minutos
      const tempoRestante = Math.max(0, tempoTotal - diff);
      return tempoRestante > 0
        ? `Previsão: ${tempoRestante} minutos`
        : 'Chegando em breve!';
    } else {
      const tempoTotal = 30; // minutos
      const tempoRestante = Math.max(0, tempoTotal - diff);
      return tempoRestante > 0
        ? `Pronto em: ${tempoRestante} minutos`
        : 'Pronto para retirada!';
    }
  };

  return (
    <div className="rastreamento-container">
      <header className="rastreamento-header">
        <h1>
          <i className="fas fa-search-location"></i>
          Rastrear Pedido
        </h1>
        <a href="/" className="btn btn-secondary">
          <i className="fas fa-arrow-left"></i>
          Voltar
        </a>
      </header>

      <div className="rastreamento-content">
        <div className="search-box">
          <form onSubmit={handleSubmit}>
            <div className="input-group">
              <input
                type="number"
                placeholder="Digite o número do pedido"
                value={pedidoId}
                onChange={(e) => setPedidoId(e.target.value)}
                className="pedido-input"
              />
              <button type="submit" className="btn" disabled={loading}>
                {loading ? (
                  <>
                    <i className="fas fa-spinner fa-spin"></i>
                    Buscando...
                  </>
                ) : (
                  <>
                    <i className="fas fa-search"></i>
                    Buscar
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {erro && (
          <div className="erro-message">
            <i className="fas fa-exclamation-circle"></i>
            {erro}
          </div>
        )}

        {pedido && (
          <div className="pedido-detalhes">
            <div className="pedido-info-card">
              <h2>Pedido #{pedido.id}</h2>
              <div className="info-grid">
                <div className="info-item">
                  <i className="fas fa-user"></i>
                  <div>
                    <span className="info-label">Cliente</span>
                    <span className="info-value">{pedido.nome_cliente}</span>
                  </div>
                </div>

                <div className="info-item">
                  <i className="fas fa-pizza-slice"></i>
                  <div>
                    <span className="info-label">Itens</span>
                    <span className="info-value">{pedido.itens}</span>
                  </div>
                </div>

                <div className="info-item">
                  <i className="fas fa-money-bill-wave"></i>
                  <div>
                    <span className="info-label">Valor Total</span>
                    <span className="info-value">R$ {pedido.valor_total.toFixed(2)}</span>
                  </div>
                </div>

                <div className="info-item">
                  <i className={pedido.tipo_entrega === 'entrega' ? 'fas fa-truck' : 'fas fa-store'}></i>
                  <div>
                    <span className="info-label">Tipo</span>
                    <span className="info-value">
                      {pedido.tipo_entrega === 'entrega' ? 'Entrega' : 'Retirada'}
                    </span>
                  </div>
                </div>

                {pedido.endereco && (
                  <div className="info-item">
                    <i className="fas fa-map-marker-alt"></i>
                    <div>
                      <span className="info-label">Endereço</span>
                      <span className="info-value">{pedido.endereco}</span>
                    </div>
                  </div>
                )}

                <div className="info-item">
                  <i className="fas fa-clock"></i>
                  <div>
                    <span className="info-label">Realizado em</span>
                    <span className="info-value">{formatarData(pedido.data_criacao)}</span>
                  </div>
                </div>
              </div>

              <div className="tempo-estimado">
                <i className="fas fa-hourglass-half"></i>
                {getTempoEstimado(pedido)}
              </div>
            </div>

            <div className="status-timeline">
              <h3>Status do Pedido</h3>
              <div className="timeline">
                {STATUS_TIMELINE.map((step, index) => {
                  const currentIndex = getCurrentStepIndex(pedido.status);
                  const isCompleted = index <= currentIndex;
                  const isCurrent = index === currentIndex;

                  return (
                    <div
                      key={step.key}
                      className={`timeline-item ${isCompleted ? 'completed' : ''} ${isCurrent ? 'current' : ''}`}
                    >
                      <div className="timeline-marker">
                        <i className={`fas fa-${step.icon}`}></i>
                      </div>
                      <div className="timeline-content">
                        <h4>{step.label}</h4>
                        {isCurrent && (
                          <span className="status-badge">Status Atual</span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Rastreamento;
