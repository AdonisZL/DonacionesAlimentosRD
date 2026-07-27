import { Routes, Route } from 'react-router-dom'
import Inicio from './paginas/Inicio.jsx'
import Login from './paginas/Login.jsx'
import Registro from './paginas/Registro.jsx'
import Perfil from './paginas/Perfil.jsx'
import MisDerechos from './paginas/MisDerechos.jsx'
import Inventario from './paginas/Inventario.jsx'
import Emparejamientos from './paginas/Emparejamientos.jsx'
import Reportes from './paginas/Reportes.jsx'
import Admin from './paginas/Admin.jsx'
import Notificaciones from './paginas/Notificaciones.jsx'
import VerificarCorreo from './paginas/VerificarCorreo.jsx'
import RecuperarPassword from './paginas/RecuperarPassword.jsx'
import RestablecerPassword from './paginas/RestablecerPassword.jsx'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Inicio />} />
      <Route path="/login" element={<Login />} />
      <Route path="/registro" element={<Registro />} />
      <Route path="/perfil" element={<Perfil />} />
      <Route path="/mis-derechos" element={<MisDerechos />} />
      <Route path="/inventario" element={<Inventario />} />
      <Route path="/emparejamientos" element={<Emparejamientos />} />
      <Route path="/reportes" element={<Reportes />} />
      <Route path="/admin" element={<Admin />} />
      <Route path="/notificaciones" element={<Notificaciones />} />
      <Route path="/verificar-correo" element={<VerificarCorreo />} />
      <Route path="/recuperar-password" element={<RecuperarPassword />} />
      <Route path="/restablecer-password" element={<RestablecerPassword />} />
    </Routes>
  )
}

export default App
