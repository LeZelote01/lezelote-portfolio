
import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

const AuthPage = () => {
  const navigate = useNavigate();
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user) navigate("/dashboard", { replace: true });
    });
    // eslint-disable-next-line
  }, []);

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMsg(null);
    try {
      if (mode === "signin") {
        // Clean up limbo states before login (important!)
        Object.keys(localStorage).forEach((key) => {
          if (key.startsWith('supabase.auth.') || key.includes('sb-')) localStorage.removeItem(key);
        });
        Object.keys(sessionStorage).forEach((key) => {
          if (key.startsWith('supabase.auth.') || key.includes('sb-')) sessionStorage.removeItem(key);
        });
        try { await supabase.auth.signOut({ scope: 'global' }); } catch {}
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) setMsg("Erreur : " + error.message);
        else window.location.href = "/dashboard";
      } else {
        // Signup with redirect
        const redirectTo = `${window.location.origin}/dashboard`;
        const { error } = await supabase.auth.signUp({ email, password, options: { emailRedirectTo: redirectTo } });
        if (error) setMsg("Erreur : " + error.message);
        else setMsg("Vérifie ta boîte mail pour le lien de validation.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-fuchsia-100 to-fuchsia-300 dark:from-fuchsia-950 dark:to-fuchsia-900">
      <Card className="w-full max-w-md p-4 shadow-2xl">
        <CardHeader>
          <CardTitle className="text-center">{mode === "signin" ? "Connexion admin" : "Créer un accès admin"}</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleAuth} className="space-y-4">
            <Input 
              type="email" 
              required
              placeholder="Adresse email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              autoComplete="email"
              className="bg-white dark:bg-fuchsia-950"
            />
            <Input 
              type="password" 
              required
              placeholder="Mot de passe"
              value={password}
              onChange={e => setPassword(e.target.value)}
              autoComplete="current-password"
              className="bg-white dark:bg-fuchsia-950"
            />
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Traitement…" : (mode === "signin" ? "Se connecter" : "Créer le compte admin")}
            </Button>
          </form>
          <div className="text-center mt-4">
            <Button
              type="button"
              size="sm"
              variant="link"
              onClick={() => setMode(mode === "signin" ? "signup" : "signin")}
            >
              {mode === "signin"
                ? "Créer un nouveau compte admin"
                : "J'ai déjà un compte admin"}
            </Button>
          </div>
          {msg && <div className="text-center mt-2 text-fuchsia-800 dark:text-fuchsia-200">{msg}</div>}
        </CardContent>
      </Card>
    </div>
  );
};
export default AuthPage;
