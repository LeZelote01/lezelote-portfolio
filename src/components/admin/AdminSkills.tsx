
const AdminSkills = () => (
  <section className="bg-card rounded-lg shadow p-6 border">
    <h2 className="font-bold text-lg mb-2">Gérer les compétences</h2>
    <p className="text-sm text-muted-foreground mb-2">⚡ Interface fictive, connecte Supabase pour persister les données.</p>
    <ul className="space-y-2">
      <li>JavaScript <button className="text-primary ml-2 text-xs underline">Modifier</button></li>
      <li>React <button className="text-primary ml-2 text-xs underline">Modifier</button></li>
      <li>Node.js <button className="text-primary ml-2 text-xs underline">Modifier</button></li>
    </ul>
    <button className="mt-4 px-4 py-2 rounded bg-primary text-primary-foreground text-sm hover:bg-primary/90">Ajouter une compétence</button>
  </section>
);
export default AdminSkills;
