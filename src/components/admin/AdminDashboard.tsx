
import AdminSkills from "./AdminSkills";
import AdminProjects from "./AdminProjects";
import CVUploader from "./CVUploader";

const AdminDashboard = () => (
  <div className="max-w-6xl mx-auto py-12 px-4">
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

export default AdminDashboard;
