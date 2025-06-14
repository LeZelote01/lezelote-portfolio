
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
      console.log("[useAuth] Auth state changed. Session:", session);
    });

    // 2. Au chargement, récupérer la session existante
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setLoading(false);
      console.log("[useAuth] Initial session loaded:", session);
    });

    return () => subscription.unsubscribe();
    // eslint-disable-next-line
  }, []);

  // 3. Check du rôle admin dès que l'utilisateur change
  useEffect(() => {
    if (!session?.user) {
      setIsAdmin(false);
      console.log("[useAuth] No user in session. isAdmin set to false.");
      return;
    }
    const checkAdmin = async () => {
      console.log("[useAuth] Checking admin role for user:", session.user.id);
      const { data, error } = await supabase.rpc("has_role", {
        _user_id: session.user.id,
        _role: "admin"
      });
      console.log("[useAuth] Result of has_role RPC — data:", data, "error:", error);
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

  // Ajout de logs pour voir exactement ce que renvoie le hook à chaque render
  console.log("[useAuth] Render — session:", session, "isAdmin:", isAdmin, "loading:", loading);

  return { session, user: session?.user, isAdmin, signOut, loading };
}
