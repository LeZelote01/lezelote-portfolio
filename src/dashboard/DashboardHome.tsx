
import DashboardLayout from "./DashboardLayout";
import { User } from "lucide-react";
import { Link } from "react-router-dom";

const DashboardHome = () => {
  return (
    <DashboardLayout>
      <div className="mx-auto max-w-2xl rounded-lg bg-white shadow p-8 dark:bg-fuchsia-900 dark:text-fuchsia-50">
        <h1 className="text-3xl font-bold mb-4 flex items-center gap-2">
          <User size={32} /> Bienvenue sur le Dashboard Admin
        </h1>
        <ul className="list-disc ml-6 mt-4 space-y-2 text-lg">
          <li>
            <Link to="/dashboard/projects" className="text-primary underline">Gérer les projets</Link>
          </li>
          <li>
            <Link to="/dashboard/skills" className="text-primary underline">Gérer les compétences</Link>
          </li>
          <li>
            <Link to="/dashboard/cv" className="text-primary underline">Gérer le CV affiché</Link>
          </li>
        </ul>
        <div className="mt-6 italic text-sm text-fuchsia-700 dark:text-fuchsia-200">
          Toutes ces sections sont strictement réservées à l’administrateur.
        </div>
      </div>
    </DashboardLayout>
  );
};

export default DashboardHome;
