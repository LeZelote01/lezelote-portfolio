import { ReactNode } from "react";
import NavbarDashboard from "./NavbarDashboard";
import FooterDashboard from "./FooterDashboard";
import { useAdminAuth } from "./useAdminAuth";

/**
 * Layout Admin Dashboard : protection d'accès + navbar et footer spécifiques.
 */
const DashboardLayout = ({ children }: { children: ReactNode }) => {
  const { loading, isAdmin } = useAdminAuth();

  if (loading) return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-fuchsia-100 to-fuchsia-200 dark:from-fuchsia-950 dark:to-fuchsia-900">
      <NavbarDashboard />
      <main className="flex-grow flex items-center justify-center">
        <span className="text-lg font-medium animate-pulse">Chargement du tableau de bord…</span>
      </main>
    </div>
  );
  if (!isAdmin) return null;

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-fuchsia-100 to-pink-100 dark:from-fuchsia-950 dark:to-fuchsia-900 transition-colors">
      <NavbarDashboard />
      <main className="flex-grow p-4 sm:p-8">
        {children}
      </main>
      <FooterDashboard />
    </div>
  );
};
export default DashboardLayout;
