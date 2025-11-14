const API_BASE_URL = 'http://localhost:5000';

export const iniciarSessao = async () => {
  const response = await fetch(`${API_BASE_URL}/iniciar_sessao`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  return response.json();
};

export const enviarMensagem = async (sessionId, mensagem) => {
  const response = await fetch(`${API_BASE_URL}/enviar_mensagem`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      session_id: sessionId,
      mensagem: mensagem,
    }),
  });
  return response.json();
};

export const iniciarPedido = async (sessionId) => {
  const response = await fetch(`${API_BASE_URL}/iniciar_pedido`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      session_id: sessionId,
    }),
  });
  return response.json();
};
