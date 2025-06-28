// frontend/src/App.tsx
import { useLocation } from 'react-router-dom';
import { AdminAuthProvider } from './contexts/AdminAuthProvider';
import { AuthProvider } from './contexts/AuthProvider';
import RouterAdmin from './routers/RouterAdmin';
import RouterCommon from './routers/RouterCommon';

function App() {
  const location = useLocation();
  const isAdminRoute = location.pathname.startsWith('/admin');

  return isAdminRoute ? (
    <AdminAuthProvider>
      <RouterAdmin />
    </AdminAuthProvider>
  ) : (
    <AuthProvider>
      <RouterCommon />
    </AuthProvider>
  );
}

export default App;
