
import AdminDashboard from "@/components/admin/AdminDashboard";
import { useAuth } from "@/hooks/useAuth";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const Dashboard = () => {
  const { user, isAdmin, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    console.log("[Dashboard] Render — user:", user, "isAdmin:", isAdmin, "loading:", loading);
    if (!loading) {
      if (!user) {
        console.log("[Dashboard] Pas d'utilisateur : redirection /login");
        navigate("/login");
      }
      else if (!isAdmin) {
        console.log("[Dashboard] Utilisateur connecté mais pas admin. Redirection /");
        navigate("/");
      } else {
        console.log("[Dashboard] Utilisateur admin : accès autorisé au dashboard.");
      }
    }
    // eslint-disable-next-line
  }, [user, isAdmin, loading]);

  if (loading || !user || !isAdmin) {
    // Loading ou redirection...
    return (
      <main className="min-h-[60vh] flex items-center justify-center">
        <div className="animate-pulse text-lg text-muted-foreground">Chargement…</div>
      </main>
    );
  }

  // Dashboard strict : pas de navbar, pas de footer, juste l’admin
  return (
    <main>
      <AdminDashboard />
    </main>
  );
};

export default Dashboard;
