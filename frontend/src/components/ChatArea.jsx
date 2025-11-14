import { useEffect, useRef } from 'react';
import Message from './Message';
import './ChatArea.css';

const ChatArea = ({ mensagens }) => {
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [mensagens]);

  return (
    <div className="chat-area">
      {mensagens.map((msg, index) => (
        <Message key={index} tipo={msg.tipo} conteudo={msg.conteudo} />
      ))}
      <div ref={chatEndRef} />
    </div>
  );
};

export default ChatArea;
