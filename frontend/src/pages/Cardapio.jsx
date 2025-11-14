import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Cardapio.css';

const API_URL = 'http://localhost:5000';

const CATEGORIAS = [
  { value: 'pizza_tradicional', label: 'Pizza Tradicional' },
  { value: 'pizza_especial', label: 'Pizza Especial' },
  { value: 'bebida', label: 'Bebida' },
  { value: 'sobremesa', label: 'Sobremesa' }
];

const Cardapio = () => {
  const [itens, setItens] = useState([]);
  const [itensFiltrados, setItensFiltrados] = useState([]);
  const [filtroCategoria, setFiltroCategoria] = useState(null);
  const [termoBusca, setTermoBusca] = useState('');
  const [mostrarForm, setMostrarForm] = useState(false);
  const [editando, setEditando] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    nome: '',
    descricao: '',
    preco: '',
    categoria: 'pizza_tradicional',
    imagem: ''
  });

  useEffect(() => {
    // Verificar autenticação
    const isAuthenticated = localStorage.getItem('adminAuth') === 'true';
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    carregarItens();
  }, [filtroCategoria]);

  const carregarItens = async () => {
    try {
      setLoading(true);
      const url = filtroCategoria
        ? `${API_URL}/admin/cardapio?categoria=${filtroCategoria}`
        : `${API_URL}/admin/cardapio`;

      const response = await fetch(url);
      const data = await response.json();

      if (data.sucesso) {
        setItens(data.itens);
        setItensFiltrados(data.itens);
      }
    } catch (error) {
      console.error('Erro ao carregar cardápio:', error);
    } finally {
      setLoading(false);
    }
  };

  // Filtrar itens com base no termo de busca
  useEffect(() => {
    if (!termoBusca.trim()) {
      setItensFiltrados(itens);
      return;
    }

    const termo = termoBusca.toLowerCase();
    const filtrados = itens.filter(item =>
      item.nome.toLowerCase().includes(termo) ||
      item.descricao?.toLowerCase().includes(termo) ||
      item.preco.toString().includes(termo)
    );

    setItensFiltrados(filtrados);
  }, [termoBusca, itens]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const url = editando
        ? `${API_URL}/admin/cardapio/${editando}`
        : `${API_URL}/admin/cardapio`;

      const method = editando ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...formData,
          preco: parseFloat(formData.preco)
        })
      });

      const data = await response.json();

      if (data.sucesso) {
        alert(data.mensagem);
        setMostrarForm(false);
        setEditando(null);
        resetForm();
        carregarItens();
      } else {
        alert(`Erro: ${data.erro}`);
      }
    } catch (error) {
      console.error('Erro ao salvar item:', error);
      alert('Erro ao salvar item');
    } finally {
      setLoading(false);
    }
  };

  const handleEditar = (item) => {
    setEditando(item.id);
    setFormData({
      nome: item.nome,
      descricao: item.descricao,
      preco: item.preco.toString(),
      categoria: item.categoria,
      imagem: item.imagem || ''
    });
    setMostrarForm(true);
  };

  const handleRemover = async (itemId) => {
    if (!confirm('Tem certeza que deseja remover este item?')) {
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/admin/cardapio/${itemId}`, {
        method: 'DELETE'
      });

      const data = await response.json();

      if (data.sucesso) {
        alert(data.mensagem);
        carregarItens();
      } else {
        alert(`Erro: ${data.erro}`);
      }
    } catch (error) {
      console.error('Erro ao remover item:', error);
      alert('Erro ao remover item');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      nome: '',
      descricao: '',
      preco: '',
      categoria: 'pizza_tradicional',
      imagem: ''
    });
  };

  const getCategoriaLabel = (categoria) => {
    const cat = CATEGORIAS.find(c => c.value === categoria);
    return cat ? cat.label : categoria;
  };

  return (
    <div className="cardapio-container">
      <header className="cardapio-header">
        <div>
          <h1>
            <i className="fas fa-utensils"></i>
            Gerenciar Cardápio
          </h1>
          <p>Total de itens: {itens.length}</p>
        </div>
        <div className="header-actions">
          <button onClick={() => navigate('/admin')} className="btn btn-secondary">
            <i className="fas fa-arrow-left"></i>
            Voltar
          </button>
          <button
            onClick={() => {
              setMostrarForm(true);
              setEditando(null);
              resetForm();
            }}
            className="btn btn-primary"
          >
            <i className="fas fa-plus"></i>
            Novo Item
          </button>
        </div>
      </header>

      {/* Barra de Busca */}
      <div className="busca-container">
        <div className="busca-input-wrapper">
          <i className="fas fa-search"></i>
          <input
            type="text"
            className="busca-input"
            placeholder="Buscar por nome, descrição ou preço..."
            value={termoBusca}
            onChange={(e) => setTermoBusca(e.target.value)}
          />
          {termoBusca && (
            <button
              className="busca-clear"
              onClick={() => setTermoBusca('')}
              title="Limpar busca"
            >
              <i className="fas fa-times"></i>
            </button>
          )}
        </div>
        {termoBusca && (
          <span className="busca-resultado">
            {itensFiltrados.length} {itensFiltrados.length === 1 ? 'resultado encontrado' : 'resultados encontrados'}
          </span>
        )}
      </div>

      {/* Filtros */}
      <div className="filtros">
        <button
          className={`filtro-btn ${filtroCategoria === null ? 'active' : ''}`}
          onClick={() => setFiltroCategoria(null)}
        >
          Todas
        </button>
        {CATEGORIAS.map(cat => (
          <button
            key={cat.value}
            className={`filtro-btn ${filtroCategoria === cat.value ? 'active' : ''}`}
            onClick={() => setFiltroCategoria(cat.value)}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Formulário */}
      {mostrarForm && (
        <div className="modal-overlay" onClick={() => setMostrarForm(false)}>
          <div className="modal-form" onClick={(e) => e.stopPropagation()}>
            <h2>
              {editando ? 'Editar Item' : 'Novo Item'}
            </h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Nome *</label>
                <input
                  type="text"
                  value={formData.nome}
                  onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Descrição</label>
                <textarea
                  value={formData.descricao}
                  onChange={(e) => setFormData({ ...formData, descricao: e.target.value })}
                  rows="3"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Preço (R$) *</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.preco}
                    onChange={(e) => setFormData({ ...formData, preco: e.target.value })}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Categoria *</label>
                  <select
                    value={formData.categoria}
                    onChange={(e) => setFormData({ ...formData, categoria: e.target.value })}
                    required
                  >
                    {CATEGORIAS.map(cat => (
                      <option key={cat.value} value={cat.value}>
                        {cat.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>URL da Imagem</label>
                <input
                  type="url"
                  value={formData.imagem}
                  onChange={(e) => setFormData({ ...formData, imagem: e.target.value })}
                  placeholder="https://exemplo.com/imagem.jpg"
                />
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  onClick={() => {
                    setMostrarForm(false);
                    setEditando(null);
                    resetForm();
                  }}
                  className="btn btn-secondary"
                >
                  Cancelar
                </button>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Salvando...' : editando ? 'Atualizar' : 'Adicionar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Lista de Itens */}
      <div className="itens-grid">
        {itensFiltrados.map(item => (
          <div key={item.id} className={`item-card ${!item.ativo ? 'inativo' : ''}`}>
            {item.imagem && (
              <div className="item-imagem">
                <img src={item.imagem} alt={item.nome} />
              </div>
            )}
            <div className="item-content">
              <div className="item-header">
                <h3>{item.nome}</h3>
                <span className="item-categoria">{getCategoriaLabel(item.categoria)}</span>
              </div>
              <p className="item-descricao">{item.descricao}</p>
              <div className="item-footer">
                <span className="item-preco">R$ {item.preco.toFixed(2)}</span>
                <div className="item-actions">
                  <button
                    onClick={() => handleEditar(item)}
                    className="btn-icon btn-edit"
                    title="Editar"
                  >
                    <i className="fas fa-edit"></i>
                  </button>
                  <button
                    onClick={() => handleRemover(item.id)}
                    className="btn-icon btn-delete"
                    title="Remover"
                  >
                    <i className="fas fa-trash"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {itensFiltrados.length === 0 && !loading && (
        <div className="empty-state">
          <i className="fas fa-utensils"></i>
          <p>{termoBusca ? 'Nenhum item corresponde à busca' : 'Nenhum item encontrado'}</p>
        </div>
      )}
    </div>
  );
};

export default Cardapio;
