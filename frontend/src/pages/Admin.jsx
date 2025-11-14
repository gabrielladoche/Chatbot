import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Admin.css';

const STATUS_OPTIONS = [
  { value: 'finalizado', label: 'Finalizado', color: '#gray' },
  { value: 'confirmado', label: 'Confirmado', color: '#2196F3' },
  { value: 'preparando', label: 'Preparando', color: '#FF9800' },
  { value: 'pronto', label: 'Pronto', color: '#4CAF50' },
  { value: 'saiu_entrega', label: 'Saiu para entrega', color: '#9C27B0' },
  { value: 'entregue', label: 'Entregue', color: '#4CAF50' },
  { value: 'cancelado', label: 'Cancelado', color: '#F44336' }
];

const API_URL = 'http://localhost:5000';

const Admin = () => {
  const [pedidos, setPedidos] = useState([]);
  const [filtro, setFiltro] = useState(null);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [initialLoading, setInitialLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Verificar autenticação
    const isAuthenticated = localStorage.getItem('adminAuth') === 'true';
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    // Simular carregamento inicial com animação
    const loadData = async () => {
      await Promise.all([carregarPedidos(), carregarEstatisticas()]);
      // Manter loading por pelo menos 2 segundos para mostrar a animação
      setTimeout(() => {
        setInitialLoading(false);
      }, 2000);
    };

    loadData();

    // Atualizar automaticamente a cada 10 segundos
    const interval = setInterval(() => {
      carregarPedidos();
      carregarEstatisticas();
    }, 10000);

    return () => clearInterval(interval);
  }, [filtro]);

  const carregarPedidos = async () => {
    try {
      const url = filtro
        ? `${API_URL}/admin/pedidos?status=${filtro}`
        : `${API_URL}/admin/pedidos`;

      const response = await fetch(url);
      const data = await response.json();

      if (data.sucesso) {
        setPedidos(data.pedidos);
      }
    } catch (error) {
      console.error('Erro ao carregar pedidos:', error);
    }
  };

  const carregarEstatisticas = async () => {
    try {
      const response = await fetch(`${API_URL}/estatisticas`);
      const data = await response.json();

      if (data.sucesso) {
        setStats(data.estatisticas);
      }
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    }
  };

  const atualizarStatus = async (pedidoId, novoStatus) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/admin/pedidos/${pedidoId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: novoStatus })
      });

      const data = await response.json();

      if (data.sucesso) {
        carregarPedidos();
        alert(`Pedido #${pedidoId} atualizado para: ${novoStatus}`);
      } else {
        alert(`Erro: ${data.erro}`);
      }
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
      alert('Erro ao atualizar status do pedido');
    } finally {
      setLoading(false);
    }
  };

  const getStatusLabel = (status) => {
    const opt = STATUS_OPTIONS.find(s => s.value === status);
    return opt ? opt.label : status;
  };

  const getStatusColor = (status) => {
    const opt = STATUS_OPTIONS.find(s => s.value === status);
    return opt ? opt.color : '#gray';
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

  const handleLogout = () => {
    localStorage.removeItem('adminAuth');
    localStorage.removeItem('adminUser');
    navigate('/login');
  };

  const adminUser = localStorage.getItem('adminUser');

  // Tela de loading com pizza girando
  if (initialLoading) {
    return (
      <div className="loading-screen">
        <div className="pizza-loader">
          <div className="pizza-slice">🍕</div>
          <div className="pizza-circle"></div>
        </div>
        <h2 className="loading-text">Preparando o painel...</h2>
        <div className="loading-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-container">
      <header className="admin-header">
        <div>
          <h1>
            <i className="fas fa-shield-alt"></i>
            Painel Administrativo
          </h1>
          {adminUser && (
            <span className="admin-user">
              <i className="fas fa-user-circle"></i>
              {adminUser}
            </span>
          )}
        </div>
        <div className="admin-header-actions">
          <a href="/admin/cardapio" className="btn btn-cardapio">
            <i className="fas fa-utensils"></i>
            Gerenciar Cardápio
          </a>
          <a href="/" className="btn btn-secondary">
            <i className="fas fa-arrow-left"></i>
            Voltar ao Site
          </a>
          <button onClick={handleLogout} className="btn btn-danger">
            <i className="fas fa-sign-out-alt"></i>
            Sair
          </button>
        </div>
      </header>

      {/* Estatísticas */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <i className="fas fa-receipt"></i>
            <div className="stat-info">
              <span className="stat-label">Total de Pedidos</span>
              <span className="stat-value">{stats.total_pedidos}</span>
            </div>
          </div>
          <div className="stat-card">
            <i className="fas fa-dollar-sign"></i>
            <div className="stat-info">
              <span className="stat-label">Faturamento Total</span>
              <span className="stat-value">R$ {stats.valor_total.toFixed(2)}</span>
            </div>
          </div>
          <div className="stat-card">
            <i className="fas fa-calendar-day"></i>
            <div className="stat-info">
              <span className="stat-label">Pedidos Hoje</span>
              <span className="stat-value">{stats.pedidos_hoje}</span>
            </div>
          </div>
          <div className="stat-card">
            <i className="fas fa-chart-line"></i>
            <div className="stat-info">
              <span className="stat-label">Ticket Médio</span>
              <span className="stat-value">R$ {stats.ticket_medio.toFixed(2)}</span>
            </div>
          </div>
        </div>
      )}

      {/* Filtros */}
      <div className="filters">
        <button
          className={`filter-btn ${filtro === null ? 'active' : ''}`}
          onClick={() => setFiltro(null)}
        >
          Todos
        </button>
        {STATUS_OPTIONS.map(opt => (
          <button
            key={opt.value}
            className={`filter-btn ${filtro === opt.value ? 'active' : ''}`}
            onClick={() => setFiltro(opt.value)}
            style={{ borderColor: opt.color }}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {/* Lista de Pedidos */}
      <div className="pedidos-list">
        <h2>Pedidos ({pedidos.length})</h2>

        {pedidos.length === 0 ? (
          <div className="empty-state">
            <i className="fas fa-inbox"></i>
            <p>Nenhum pedido encontrado</p>
          </div>
        ) : (
          <div className="pedidos-grid">
            {pedidos.map(pedido => (
              <div key={pedido.id} className="pedido-card">
                <div className="pedido-header">
                  <div>
                    <h3>Pedido #{pedido.id}</h3>
                    <span className="pedido-cliente">
                      <i className="fas fa-user"></i>
                      {pedido.nome_cliente}
                    </span>
                  </div>
                  <span
                    className="pedido-status-badge"
                    style={{ background: getStatusColor(pedido.status) }}
                  >
                    {getStatusLabel(pedido.status)}
                  </span>
                </div>

                <div className="pedido-body">
                  <div className="pedido-info">
                    <i className="fas fa-pizza-slice"></i>
                    <span>{pedido.itens}</span>
                  </div>

                  <div className="pedido-info">
                    <i className="fas fa-money-bill-wave"></i>
                    <span>
                      R$ {pedido.valor_total.toFixed(2)}
                      {pedido.taxa_entrega > 0 && (
                        <small> (+ R$ {pedido.taxa_entrega.toFixed(2)} entrega)</small>
                      )}
                    </span>
                  </div>

                  <div className="pedido-info">
                    <i className="fas fa-credit-card"></i>
                    <span>{pedido.forma_pagamento}</span>
                  </div>

                  <div className="pedido-info">
                    <i className={pedido.tipo_entrega === 'entrega' ? 'fas fa-truck' : 'fas fa-store'}></i>
                    <span>
                      {pedido.tipo_entrega === 'entrega' ? 'Entrega' : 'Retirada'}
                    </span>
                  </div>

                  {pedido.endereco && (
                    <div className="pedido-info">
                      <i className="fas fa-map-marker-alt"></i>
                      <span>{pedido.endereco}</span>
                    </div>
                  )}

                  <div className="pedido-info">
                    <i className="fas fa-clock"></i>
                    <span>{formatarData(pedido.data_criacao)}</span>
                  </div>
                </div>

                <div className="pedido-footer">
                  <label>Atualizar Status:</label>
                  <select
                    value={pedido.status}
                    onChange={(e) => atualizarStatus(pedido.id, e.target.value)}
                    disabled={loading}
                    className="status-select"
                  >
                    {STATUS_OPTIONS.map(opt => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Admin;
