
import { Link, useLocation } from "react-router-dom";
import { FileText, Home, User, Image, Contact as ContactIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import CVDownloadButton from "./CVDownloadButton";

const NAV_LINKS = [
  { label: "Accueil", to: "/", icon: Home },
  { label: "Compétences", to: "/skills", icon: FileText },
  { label: "Projets", to: "/projects", icon: Image },
  { label: "À propos", to: "/about", icon: User },
  { label: "Contact", to: "/contact", icon: ContactIcon }
];

const Navbar = () => {
  const { pathname } = useLocation();
  return (
    <nav className="sticky top-0 z-50 w-full bg-background border-b border-border">
      <div className="max-w-7xl mx-auto flex items-center justify-between px-8 py-3">
        <div className="flex items-center gap-6">
          <span className="font-bold text-2xl tracking-tight text-primary">Mon Portfolio</span>
          <ul className="flex items-center gap-2">
            {NAV_LINKS.map(({ label, to, icon: Icon }) => (
              <li key={to}>
                <Link
                  to={to}
                  className={cn(
                    "flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors hover:bg-primary/10 hover:text-primary",
                    pathname === to && "bg-primary text-primary-foreground shadow"
                  )}
                >
                  <Icon size={18} className="mr-2" />
                  {label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
        <div className="flex items-center gap-4">
          <CVDownloadButton />
          <Link to="/dashboard" className="font-semibold text-muted-foreground underline opacity-70 hover:opacity-100 text-xs">
            Admin
          </Link>
        </div>
      </div>
    </nav>
  );
};
export default Navbar;
