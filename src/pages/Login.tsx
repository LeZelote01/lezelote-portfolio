
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/hooks/useAuth";

const Login = () => {
  const { session, loading } = useAuth();
  const navigate = useNavigate();

  const [isSignup, setIsSignup] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  // Si déjà connecté, redirige vers dashboard ou vers /
  if (!loading && session) {
    navigate("/dashboard");
    return null;
  }

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setMessage("");

    if (isSignup) {
      // SIGN UP
      const { error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          emailRedirectTo: `${window.location.origin}/dashboard`
        }
      });
      if (error) setError(error.message);
      else setMessage("Vérifie ta boîte mail pour confirmer ton inscription !");
    } else {
      // SIGN IN
      const { error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });
      if (error) setError(error.message);
      else {
        setMessage("Connexion réussie !");
        // Redirection après login : le hook useAuth s'en chargera
      }
    }
  };

  return (
    <>
      <Navbar />
      <main className="min-h-[60vh] flex items-center justify-center">
        <form
          className="w-full max-w-sm bg-card p-8 shadow-md rounded space-y-4 border"
          onSubmit={handleAuth}
        >
          <h2 className="text-xl font-bold mb-2 text-center">
            {isSignup ? "Créer un compte admin" : "Connexion administrateur"}
          </h2>
          <div>
            <label className="block text-sm font-semibold mb-1" htmlFor="email">
              Email
            </label>
            <Input
              id="email"
              type="email"
              placeholder="Votre email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              autoComplete="username"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-1" htmlFor="password">
              Mot de passe
            </label>
            <Input
              id="password"
              type="password"
              placeholder="Votre mot de passe"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>
          {error && (
            <div className="text-red-600 text-sm text-center">{error}</div>
          )}
          {message && (
            <div className="text-green-700 text-sm text-center">{message}</div>
          )}
          <Button type="submit" className="w-full">
            {isSignup ? "Créer le compte" : "Se connecter"}
          </Button>
          <div className="text-center mt-2">
            <button
              type="button"
              className="text-xs underline text-primary"
              onClick={() => {
                setError("");
                setMessage("");
                setIsSignup(x => !x);
              }}
            >
              {isSignup ? "Déjà un compte ? Se connecter" : "Pas encore de compte ? S’inscrire"}
            </button>
          </div>
        </form>
      </main>
      <Footer />
    </>
  );
};

export default Login;
