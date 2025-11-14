import './CardapioDisplay.css';

const CardapioDisplay = ({ cardapio }) => {
  return (
    <div className="card animated">
      <div className="card-header">
        <i className="fas fa-clipboard-list"></i>
        <span>Cardápio</span>
      </div>
      <div className="card-body">
        <div className="cardapio-container">
          <pre>{cardapio}</pre>
        </div>
      </div>
    </div>
  );
};

export default CardapioDisplay;
