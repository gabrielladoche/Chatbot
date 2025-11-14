import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Admin from './pages/Admin';
import Rastreamento from './pages/Rastreamento';
import Login from './pages/Login';
import Cardapio from './pages/Cardapio';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/admin/cardapio" element={<Cardapio />} />
        <Route path="/rastreamento" element={<Rastreamento />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
