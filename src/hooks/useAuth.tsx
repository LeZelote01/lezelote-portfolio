
import { useState, useEffect, useCallback } from "react";
import { supabase } from "@/integrations/supabase/client";

export function useAuth() {
  const [session, setSession] = useState<null | Awaited<ReturnType<typeof supabase.auth.getSession>>["data"]["session"]>(null);
  const [loading, setLoading] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    // 1. Abonnement aux changements d’auth
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    // 2. Au chargement, récupérer la session existante
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setLoading(false);
    });

    return () => subscription.unsubscribe();
    // eslint-disable-next-line
  }, []);

  // 3. Check du rôle admin dès que l'utilisateur change
  useEffect(() => {
    if (!session?.user) {
      setIsAdmin(false);
      return;
    }
    const checkAdmin = async () => {
      // Appel la fonction Postgres pour vérifier le rôle admin côté serveur
      const { data, error } = await supabase.rpc("has_role", {
        _user_id: session.user.id,
        _role: "admin"
      });
      setIsAdmin(!error && !!data);
    };
    checkAdmin();
  }, [session]);

  const signOut = useCallback(async () => {
    await supabase.auth.signOut();
    setSession(null);
    setIsAdmin(false);
    window.location.href = "/login";
  }, []);

  return { session, user: session?.user, isAdmin, signOut, loading };
}
