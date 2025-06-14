
import { Link, useLocation } from "react-router-dom";
import { FileText, Home, User, Image, Contact as ContactIcon, Menu } from "lucide-react";
import { cn } from "@/lib/utils";
import CVDownloadButton from "./CVDownloadButton";
import ThemeToggle from "./ThemeToggle";
import LanguageSwitcher from "./LanguageSwitcher";
import { useTranslation } from "react-i18next";
import {
  Sheet,
  SheetTrigger,
  SheetContent,
  SheetClose,
} from "@/components/ui/sheet";
import { useState } from "react";

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
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-border bg-background/95 dark:bg-background/90 transition-colors duration-500 shadow-lg backdrop-blur">
      <div className="max-w-7xl mx-auto flex flex-col gap-3 sm:flex-row items-center justify-between px-2 sm:px-8 py-3">
        {/* Logo & Title */}
        <div className="flex items-center justify-between w-full sm:w-auto">
          <span className="font-bold text-xl sm:text-2xl tracking-tight text-primary drop-shadow-lg text-center sm:text-left">
            Mon Portfolio
          </span>
          {/* Hamburger only on mobile */}
          <div className="sm:hidden flex items-center">
            <Sheet open={menuOpen} onOpenChange={setMenuOpen}>
              <SheetTrigger aria-label="Ouvrir le menu de navigation" className="p-2 rounded-md hover:bg-white/30 dark:hover:bg-fuchsia-900/30 transition">
                <Menu size={28} />
              </SheetTrigger>
              <SheetContent side="left" className="sm:hidden w-64 p-0">
                <nav className="h-full flex flex-col justify-between py-4">
                  <div>
                    <div className="flex items-center justify-between px-5">
                      <span className="font-semibold text-lg">Mon Portfolio</span>
                    </div>
                    <ul className="mt-6 flex flex-col gap-1">
                      {NAV_LINKS.map(({ labelKey, to, icon: Icon }) => (
                        <li key={to}>
                          <SheetClose asChild>
                            <Link
                              to={to}
                              tabIndex={0}
                              className={cn(
                                "flex items-center px-6 py-3 text-base font-medium transition-colors hover:bg-fuchsia-100/80 dark:hover:bg-fuchsia-950/40 focus:bg-fuchsia-100 focus:text-fuchsia-900 outline-none",
                                pathname === to
                                  ? "bg-fuchsia-600 text-white shadow-md dark:bg-fuchsia-900/80"
                                  : "text-fuchsia-900 dark:text-white"
                              )}
                              onClick={() => setMenuOpen(false)}
                            >
                              <Icon size={18} className="mr-3" />
                              {t(labelKey)}
                            </Link>
                          </SheetClose>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="flex flex-col px-6 gap-2 mt-4 border-t border-border pt-4">
                    <ThemeToggle />
                    <LanguageSwitcher />
                    <CVDownloadButton />
                  </div>
                </nav>
              </SheetContent>
            </Sheet>
          </div>
        </div>
        {/* Desktop Nav */}
        <div className="flex flex-col sm:flex-row items-center gap-2 sm:gap-6 w-full mt-2 sm:mt-0 sm:w-auto">
          <ul className="hidden sm:flex flex-wrap justify-center items-center gap-1 sm:gap-2 w-full sm:w-auto">
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
          {/* Desktop Actions: right (hide on mobile) */}
          <div className="hidden sm:flex items-center gap-1 sm:gap-2">
            <ThemeToggle />
            <LanguageSwitcher />
            <CVDownloadButton />
          </div>
        </div>
      </div>
    </nav>
  );
};
export default Navbar;
