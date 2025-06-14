
import { Home, User, LogOut } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useAdminAuth } from "./useAdminAuth";

const NavbarDashboard = () => {
  const { handleLogout } = useAdminAuth();
  return (
    <nav className="w-full bg-fuchsia-900 text-white shadow-lg px-4 py-3 flex items-center justify-between">
      <Link to="/dashboard" className="font-bold text-xl">Admin Dashboard</Link>
      <div className="flex gap-4 items-center">
        <Link to="/" className="hover:underline flex gap-2 items-center"><Home size={18}/>Retour au site</Link>
        <button onClick={handleLogout} className="flex items-center gap-1 hover:underline focus:outline-none">
          <LogOut size={18} /> Déconnexion
        </button>
      </div>
    </nav>
  );
};
export default NavbarDashboard;
