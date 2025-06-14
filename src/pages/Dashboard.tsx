
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import AdminDashboard from "@/components/admin/AdminDashboard";
import { useAuth } from "@/hooks/useAuth";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const Dashboard = () => {
  const { user, isAdmin, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading) {
      if (!user) navigate("/login");
      else if (!isAdmin) navigate("/");
    }
    // eslint-disable-next-line
  }, [user, isAdmin, loading]);

  if (loading || !user || !isAdmin) {
    // Loading ou redirection...
    return (
      <>
        <Navbar />
        <main className="min-h-[60vh] flex items-center justify-center">
          <div className="animate-pulse text-lg text-muted-foreground">Chargement…</div>
        </main>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Navbar />
      <main>
        <AdminDashboard />
      </main>
      <Footer />
    </>
  );
};

export default Dashboard;
