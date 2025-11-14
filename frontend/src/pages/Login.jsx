import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';

const Login = () => {
  const [usuario, setUsuario] = useState('');
  const [senha, setSenha] = useState('');
  const [erro, setErro] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    setErro('');
    setLoading(true);

    // Simular delay de autenticação
    setTimeout(() => {
      if (usuario === 'gabriel' && senha === 'amor123') {
        // Salvar no localStorage que está autenticado
        localStorage.setItem('adminAuth', 'true');
        localStorage.setItem('adminUser', usuario);
        navigate('/admin');
      } else {
        setErro('Usuário ou senha incorretos');
        setLoading(false);
      }
    }, 500);
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-header">
          <i className="fas fa-shield-alt"></i>
          <h1>Painel Administrativo</h1>
          <p>Pizzaria</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="usuario">
              <i className="fas fa-user"></i>
              Usuário
            </label>
            <input
              type="text"
              id="usuario"
              value={usuario}
              onChange={(e) => setUsuario(e.target.value)}
              placeholder="Digite seu usuário"
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="senha">
              <i className="fas fa-lock"></i>
              Senha
            </label>
            <input
              type="password"
              id="senha"
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              placeholder="Digite sua senha"
              required
            />
          </div>

          {erro && (
            <div className="erro-message">
              <i className="fas fa-exclamation-circle"></i>
              {erro}
            </div>
          )}

          <button type="submit" className="btn-login" disabled={loading}>
            {loading ? (
              <>
                <i className="fas fa-spinner fa-spin"></i>
                Entrando...
              </>
            ) : (
              <>
                <i className="fas fa-sign-in-alt"></i>
                Entrar
              </>
            )}
          </button>
        </form>

        <div className="login-footer">
          <a href="/" className="back-link">
            <i className="fas fa-arrow-left"></i>
            Voltar ao site
          </a>
        </div>
      </div>

      <div className="login-info">
        <div className="info-card">
          <i className="fas fa-info-circle"></i>
          <p>Acesso restrito apenas para administradores</p>
        </div>
      </div>
    </div>
  );
};

export default Login;
