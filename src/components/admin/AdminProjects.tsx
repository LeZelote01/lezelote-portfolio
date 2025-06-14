
const AdminProjects = () => (
  <section className="bg-card rounded-lg shadow p-6 border">
    <h2 className="font-bold text-lg mb-2">Gérer les projets</h2>
    <p className="text-sm text-muted-foreground mb-2">⚡ Interface fictive, connecte Supabase pour persister les données.</p>
    <ul className="space-y-2">
      <li>Super projet SaaS <button className="text-primary ml-2 text-xs underline">Éditer</button></li>
      <li>Portfolio interactif <button className="text-primary ml-2 text-xs underline">Éditer</button></li>
      <li>Dashboard CRM <button className="text-primary ml-2 text-xs underline">Éditer</button></li>
    </ul>
    <button className="mt-4 px-4 py-2 rounded bg-primary text-primary-foreground text-sm hover:bg-primary/90">Ajouter un projet</button>
  </section>
);
export default AdminProjects;
