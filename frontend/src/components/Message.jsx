import './Message.css';

const Message = ({ tipo, conteudo }) => {
  return (
    <div className={`message ${tipo}-message`}>
      {tipo === 'assistant' && <strong>Atendente:</strong>}
      <div className="message-content">
        {conteudo.split('\n').map((line, index) => (
          <span key={index}>
            {line}
            {index < conteudo.split('\n').length - 1 && <br />}
          </span>
        ))}
      </div>
    </div>
  );
};

export default Message;
