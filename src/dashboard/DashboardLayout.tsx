
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
    <div className="min-h-screen flex items-center justify-center">
      <span className="animate-pulse text-lg font-medium">Chargement…</span>
    </div>
  );
  if (!isAdmin) return null;

  return (
    <div className="min-h-screen flex flex-col bg-fuchsia-50 dark:bg-fuchsia-950">
      <NavbarDashboard />
      <main className="flex-grow p-4">
        {children}
      </main>
      <FooterDashboard />
    </div>
  );
};
export default DashboardLayout;
