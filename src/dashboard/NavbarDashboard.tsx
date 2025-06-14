
import { Link, useLocation } from "react-router-dom";

const navs = [
  { href: "/dashboard", label: "Accueil" },
  { href: "/dashboard/projects", label: "Projets" },
  { href: "/dashboard/skills", label: "Compétences" },
  { href: "/dashboard/cv", label: "CV" },
];

const NavbarDashboard = () => {
  const location = useLocation();
  return (
    <nav className="w-full bg-fuchsia-900 text-white shadow-lg px-4 py-3 flex items-center justify-between">
      <Link to="/dashboard" className="font-bold text-xl">Admin Dashboard</Link>
      <div className="flex items-center space-x-6">
        {navs.map(nav => (
          <Link
            key={nav.href}
            to={nav.href}
            className={`hover:underline transition-all ${location.pathname === nav.href ? "font-bold underline" : ""}`}
          >
            {nav.label}
          </Link>
        ))}
      </div>
    </nav>
  );
};

export default NavbarDashboard;
