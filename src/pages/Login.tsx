
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

const ADMIN_EMAIL = "admin@portfolio.com";
const ADMIN_PASSWORD = "admin123"; // À remplacer par sécurisation ultérieure

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email === ADMIN_EMAIL && password === ADMIN_PASSWORD) {
      setError("");
      navigate("/dashboard");
    } else {
      setError("Identifiants invalides");
    }
  };

  return (
    <>
      <Navbar />
      <main className="min-h-[60vh] flex items-center justify-center">
        <form
          className="w-full max-w-sm bg-card p-8 shadow-md rounded space-y-4 border"
          onSubmit={handleSubmit}
        >
          <h2 className="text-xl font-bold mb-2 text-center">Connexion administrateur</h2>
          <div>
            <label className="block text-sm font-semibold mb-1" htmlFor="email">
              Email
            </label>
            <Input
              id="email"
              type="email"
              placeholder="admin@portfolio.com"
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
          <Button type="submit" className="w-full">
            Se connecter
          </Button>
        </form>
      </main>
      <Footer />
    </>
  );
};

export default Login;
