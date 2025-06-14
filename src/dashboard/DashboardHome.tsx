
import DashboardLayout from "./DashboardLayout";
import { User } from "lucide-react";
import { Link } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const DashboardHome = () => {
  return (
    <DashboardLayout>
      <div className="mx-auto max-w-2xl">
        <Card className="rounded-xl bg-white dark:bg-fuchsia-900/95 shadow-2xl p-8">
          <h1 className="text-4xl font-black text-fuchsia-900 dark:text-fuchsia-100 mb-6 flex items-center gap-3 tracking-tight">
            <User size={38} className="bg-fuchsia-200 dark:bg-fuchsia-800 rounded-full p-2" /> Bienvenue admin
          </h1>
          <div className="grid gap-4">
            <Link to="/dashboard/projects">
              <Button className="w-full font-semibold shadow bg-primary hover:bg-primary/80 rounded-lg py-4 text-lg">
                Gérer les projets
              </Button>
            </Link>
            <Link to="/dashboard/skills">
              <Button className="w-full font-semibold shadow bg-primary hover:bg-primary/80 rounded-lg py-4 text-lg">
                Gérer les compétences
              </Button>
            </Link>
            <Link to="/dashboard/cv">
              <Button variant="secondary" className="w-full font-semibold shadow rounded-lg py-4 text-lg">
                Gérer le CV affiché
              </Button>
            </Link>
          </div>
          <div className="mt-8 text-center italic text-sm text-fuchsia-700 dark:text-fuchsia-200">
            Toutes ces sections sont réservées à l’administrateur.
          </div>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default DashboardHome;
