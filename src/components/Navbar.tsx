
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
      <div className="max-w-7xl mx-auto flex flex-col gap-3 sm:flex-row items-center justify-between px-2 sm:px-8 py-3">
        <div className="flex flex-col sm:flex-row items-center gap-2 sm:gap-6 w-full">
          <span className="font-bold text-xl sm:text-2xl tracking-tight text-white drop-shadow-lg text-center sm:text-left w-full sm:w-auto">Mon Portfolio</span>
          <ul className="flex flex-wrap justify-center items-center gap-1 sm:gap-2 w-full sm:w-auto">
            {NAV_LINKS.map(({ labelKey, to, icon: Icon }) => (
              <li key={to}>
                <Link
                  to={to}
                  className={cn(
                    "flex items-center px-3 py-2 sm:px-4 rounded-md text-xs sm:text-sm font-medium transition-all hover:bg-white/40 hover:text-fuchsia-900 dark:hover:bg-fuchsia-900/40 dark:hover:text-fuchsia-200",
                    pathname === to
                      ? "bg-fuchsia-600 text-white shadow-lg dark:bg-fuchsia-900/80 dark:text-white"
                      : "text-fuchsia-900 dark:text-white"
                  )}
                >
                  <Icon size={16} className="mr-1 sm:mr-2" />
                  {t(labelKey)}
                </Link>
              </li>
            ))}
          </ul>
        </div>
        <div className="flex items-center gap-1 sm:gap-2 mt-1 sm:mt-0">
          <ThemeToggle />
          <LanguageSwitcher />
          <CVDownloadButton />
        </div>
      </div>
    </nav>
  );
};
export default Navbar;
