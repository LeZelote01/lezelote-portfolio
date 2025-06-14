
import { Link, useLocation } from "react-router-dom";
import { LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAdminAuth } from "./useAdminAuth";

const navs = [
  { href: "/dashboard", label: "Accueil" },
  { href: "/dashboard/projects", label: "Projets" },
  { href: "/dashboard/skills", label: "Compétences" },
  { href: "/dashboard/cv", label: "CV" },
];

const NavbarDashboard = () => {
  const location = useLocation();
  const { handleLogout } = useAdminAuth();

  return (
    <nav className="w-full bg-fuchsia-900 text-white shadow-xl px-4 py-3 flex items-center justify-between">
      <Link to="/dashboard" className="font-extrabold text-2xl tracking-tight flex items-center gap-2 hover:opacity-90">
        Admin <span className="bg-white text-fuchsia-900 px-2 py-0.5 rounded-lg text-sm">Dashboard</span>
      </Link>
      <div className="flex items-center space-x-6">
        {navs.map(nav => (
          <Link
            key={nav.href}
            to={nav.href}
            className={`hover:underline transition-all text-lg px-2 py-0.5 rounded ${
              location.pathname === nav.href ? "font-bold underline bg-fuchsia-200/30" : ""
            }`}
          >
            {nav.label}
          </Link>
        ))}
        <Button
          size="sm"
          variant="destructive"
          className="ml-4 flex items-center gap-2"
          onClick={handleLogout}
          title="Déconnexion"
        >
          <LogOut size={18} /> Déconnexion
        </Button>
      </div>
    </nav>
  );
};

export default NavbarDashboard;
