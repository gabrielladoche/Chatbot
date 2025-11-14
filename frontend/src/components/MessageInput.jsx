import { useState } from 'react';
import './MessageInput.css';

const MessageInput = ({ onEnviar, loading }) => {
  const [mensagem, setMensagem] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (mensagem.trim() && !loading) {
      onEnviar(mensagem);
      setMensagem('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="input-area">
      <input
        type="text"
        value={mensagem}
        onChange={(e) => setMensagem(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Digite sua mensagem..."
        className="message-input"
        disabled={loading}
      />
      <button type="submit" className="btn btn-icon" disabled={loading}>
        {loading ? (
          <div className="spinner"></div>
        ) : (
          <i className="fas fa-paper-plane"></i>
        )}
      </button>
    </form>
  );
};

export default MessageInput;
