
import AdminDashboard from "@/components/admin/AdminDashboard";
import { useAuth } from "@/hooks/useAuth";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const Dashboard = () => {
  const { user, isAdmin, loading } = useAuth();
  const navigate = useNavigate();
  const [triedRedirect, setTriedRedirect] = useState(false); // debug: pour voir si on a déjà tenté une redirection

  useEffect(() => {
    console.log("[Dashboard] Render — user:", user, "isAdmin:", isAdmin, "loading:", loading);
    if (!loading) {
      if (!user) {
        console.log("[Dashboard] Pas d'utilisateur : redirection /login");
        setTriedRedirect(true);
        navigate("/login");
      }
      else if (!isAdmin) {
        console.log("[Dashboard] Utilisateur connecté mais pas admin. Redirection /");
        setTriedRedirect(true);
        navigate("/");
      } else {
        console.log("[Dashboard] Utilisateur admin : accès autorisé au dashboard.");
        setTriedRedirect(false);
      }
    }
    // eslint-disable-next-line
  }, [user, isAdmin, loading, navigate]);

  // Version plus tolérante : tant que loading, on affiche chargement, sinon on laisse passer admin
  if (loading) {
    return (
      <main className="min-h-[60vh] flex items-center justify-center">
        <div className="animate-pulse text-lg text-muted-foreground">Chargement… (auth en cours)</div>
      </main>
    );
  }

  // Après le loading : si pas user/admin -> le useEffect va faire une redirection, sinon on laisse l’accès
  if (!user || !isAdmin) {
    return (
      <main className="min-h-[60vh] flex items-center justify-center">
        <div className="animate-pulse text-lg text-red-500">
          Vérification de l’accès… (tu n'as pas le droit, en principe redirection)
          {triedRedirect && (
            <div className="text-xs mt-2 text-muted-foreground">Redirection tentée (check console logs). Si tu vois ce message, problème de navigation !</div>
          )}
        </div>
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
