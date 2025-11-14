import { useState, useEffect } from 'react';
import CardapioGrid from './CardapioGrid';
import './CardapioModal.css';

const API_URL = 'http://localhost:5000';

const CardapioModal = ({ isOpen, onClose }) => {
  const [cardapio, setCardapio] = useState({
    pizzas_tradicionais: [],
    pizzas_especiais: [],
    bebidas: [],
    sobremesas: []
  });
  const [loading, setLoading] = useState(false);

  // Carregar cardápio da API
  useEffect(() => {
    if (isOpen) {
      carregarCardapio();
    }
  }, [isOpen]);

  const carregarCardapio = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/cardapio`);
      const data = await response.json();

      if (data.sucesso) {
        setCardapio(data.cardapio);
      }
    } catch (error) {
      console.error('Erro ao carregar cardápio:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fechar modal com ESC
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      window.addEventListener('keydown', handleEsc);
      document.body.style.overflow = 'hidden'; // Prevenir scroll do body
    }
    return () => {
      window.removeEventListener('keydown', handleEsc);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>
            <i className="fas fa-utensils"></i>
            Cardápio Completo
          </h2>
          <button className="modal-close" onClick={onClose}>
            <i className="fas fa-times"></i>
          </button>
        </div>
        <div className="modal-body">
          {loading ? (
            <div className="loading-cardapio">
              <i className="fas fa-spinner fa-spin"></i>
              <p>Carregando cardápio...</p>
            </div>
          ) : (
            <>
              <CardapioGrid
                categoria="pizzas"
                titulo="PIZZAS TRADICIONAIS"
                itens={cardapio.pizzas_tradicionais}
              />
              <CardapioGrid
                categoria="pizzas"
                titulo="PIZZAS ESPECIAIS"
                itens={cardapio.pizzas_especiais}
              />
              <CardapioGrid
                categoria="bebidas"
                titulo="BEBIDAS"
                itens={cardapio.bebidas}
              />
              <CardapioGrid
                categoria="sobremesas"
                titulo="SOBREMESAS (PIZZA DOCE)"
                itens={cardapio.sobremesas}
              />
            </>
          )}
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
};

export default CardapioModal;
