
import DashboardLayout from "./DashboardLayout";
import { User } from "lucide-react";

const DashboardHome = () => {
  return (
    <DashboardLayout>
      <div className="mx-auto max-w-2xl rounded-lg bg-white shadow p-8 dark:bg-fuchsia-900 dark:text-fuchsia-50">
        <h1 className="text-3xl font-bold mb-4 flex items-center gap-2">
          <User size={32} /> Bienvenue sur le Dashboard Admin
        </h1>
        <p className="text-lg mb-2">
          Cet espace est strictement réservé à l’administrateur. Toutes les opérations critiques (ajout/suppression/édition) sont sécurisées.
        </p>
        {/* À compléter : liste des blocs/fonctions d’administration */}
        <ul className="list-disc ml-6 mt-4">
          <li>Gérer les compétences</li>
          <li>Gérer les projets</li>
          <li>Voir les messages de contact</li>
          <li>Mettre à jour le CV affiché, etc.</li>
        </ul>
        <div className="mt-6 italic text-sm text-fuchsia-700 dark:text-fuchsia-200">
          Pour ajouter plus de fonctionnalités, dis-le simplement en chat.
        </div>
      </div>
    </DashboardLayout>
  );
};
export default DashboardHome;
