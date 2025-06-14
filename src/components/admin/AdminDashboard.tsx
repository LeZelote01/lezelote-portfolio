
import { useAuth } from "@/hooks/useAuth";
import AdminSkills from "./AdminSkills";
import AdminProjects from "./AdminProjects";
import CVUploader from "./CVUploader";
import { Button } from "@/components/ui/button";

const AdminDashboard = () => {
  const { user, signOut } = useAuth();

  return (
    <div className="max-w-6xl mx-auto py-12 px-4 relative">
      {user && (
        <div className="absolute top-4 right-4">
          <Button
            variant="destructive"
            size="sm"
            onClick={signOut}
            className="font-semibold"
          >
            Déconnexion
          </Button>
        </div>
      )}
      <h1 className="text-3xl font-bold mb-6 text-primary">Dashboard d’administration</h1>
      <div className="grid md:grid-cols-2 gap-8">
        <AdminSkills />
        <AdminProjects />
      </div>
      <div className="mt-8">
        <CVUploader />
      </div>
    </div>
  );
};

export default AdminDashboard;
