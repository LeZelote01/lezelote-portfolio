
import { Link, useLocation } from "react-router-dom";
import { FileText, Home, User, Image, Contact as ContactIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import CVDownloadButton from "./CVDownloadButton";
import ThemeToggle from "./ThemeToggle";
import LanguageSwitcher from "./LanguageSwitcher";
import { useTranslation } from "react-i18next";

const NAV_LINKS = [
  { labelKey: "navbar.home", to: "/", icon: Home },
  { labelKey: "navbar.skills", to: "/skills", icon: FileText },
  { labelKey: "navbar.projects", to: "/projects", icon: Image },
  { labelKey: "navbar.about", to: "/about", icon: User },
  { labelKey: "navbar.contact", to: "/contact", icon: ContactIcon }
];

const Navbar = () => {
  const { pathname } = useLocation();
  const { t } = useTranslation();
  return (
    <nav className="sticky top-0 z-50 w-full border-b border-border bg-gradient-to-r from-fuchsia-400/80 via-sky-300/80 to-indigo-400/80 dark:from-slate-900 dark:via-indigo-900 dark:to-fuchsia-900 transition-colors duration-500 shadow-lg">
      <div className="max-w-7xl mx-auto flex items-center justify-between px-8 py-3">
        <div className="flex items-center gap-6">
          <span className="font-bold text-2xl tracking-tight text-white drop-shadow-lg">Mon Portfolio</span>
          <ul className="flex items-center gap-2">
            {NAV_LINKS.map(({ labelKey, to, icon: Icon }) => (
              <li key={to}>
                <Link
                  to={to}
                  className={cn(
                    "flex items-center px-4 py-2 rounded-md text-sm font-medium transition-all hover:bg-white/40 hover:text-fuchsia-900 dark:hover:bg-fuchsia-900/40 dark:hover:text-fuchsia-200",
                    pathname === to
                      ? "bg-fuchsia-600 text-white shadow-lg dark:bg-fuchsia-900/80 dark:text-white"
                      : "text-fuchsia-900 dark:text-white"
                  )}
                >
                  <Icon size={18} className="mr-2" />
                  {t(labelKey)}
                </Link>
              </li>
            ))}
          </ul>
        </div>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <LanguageSwitcher />
          <CVDownloadButton />
        </div>
      </div>
    </nav>
  );
};
export default Navbar;
