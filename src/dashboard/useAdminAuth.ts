
import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useNavigate } from "react-router-dom";

/**
 * Vérifie si l'utilisateur est connecté et possède le rôle "admin".
 * Redirige vers '/' si non autorisé.
 */
export function useAdminAuth() {
  const [loading, setLoading] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    let ignore = false;
    async function check() {
      setLoading(true);
      // Vérifier session
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) {
        navigate("/", { replace: true });
        return;
      }
      // Vérifier rôle admin via Edge Function ou RPC (ici via RPC existant)
      const { data, error } = await supabase.rpc("has_role", {
        _user_id: session.user.id,
        _role: "admin",
      });
      if (ignore) return;
      if (error || !data) {
        navigate("/", { replace: true });
        return;
      }
      setIsAdmin(true);
      setLoading(false);
    }
    check();
    return () => { ignore = true; };
  }, [navigate]);

  // Fonction logout robuste (cf instructions sécurité limbo)
  const handleLogout = async () => {
    try {
      // Remove supabase tokens from storage and session
      Object.keys(localStorage).forEach((key) => {
        if (key.startsWith('supabase.auth.') || key.includes('sb-')) localStorage.removeItem(key);
      });
      Object.keys(sessionStorage).forEach((key) => {
        if (key.startsWith('supabase.auth.') || key.includes('sb-')) sessionStorage.removeItem(key);
      });
      await supabase.auth.signOut({ scope: "global" });
    } catch {}
    window.location.href = "/";
  };

  return { loading, isAdmin, handleLogout };
}
