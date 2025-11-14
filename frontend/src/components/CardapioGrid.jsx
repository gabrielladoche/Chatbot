import React from 'react';
import './CardapioGrid.css';

const CardapioGrid = ({ categoria, titulo, itens }) => {
  return (
    <div className="cardapio-section">
      <h3 className="section-title">
        {categoria === 'pizzas' && '🍕'}
        {categoria === 'bebidas' && '🥤'}
        {categoria === 'sobremesas' && '🍫'}
        {' '}{titulo}
      </h3>
      <div className="cardapio-grid">
        {itens.map((item) => (
          <div key={item.id} className="menu-item">
            <div className="item-image-container">
              <img
                src={item.imagem}
                alt={item.nome}
                className="item-image"
                loading="lazy"
              />
              <div className="item-price-badge">
                R$ {item.preco.toFixed(2).replace('.', ',')}
              </div>
            </div>
            <div className="item-info">
              <h4 className="item-name">{item.nome}</h4>
              <p className="item-description">{item.descricao}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CardapioGrid;
