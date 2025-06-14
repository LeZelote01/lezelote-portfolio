
const CVUploader = () => (
  <section className="bg-card rounded-lg shadow p-6 border">
    <h2 className="font-bold text-lg mb-2">Télécharger/Mettre à jour le CV</h2>
    <p className="text-sm text-muted-foreground mb-2">⚡ (Fictif, connecte Supabase pour gérer le fichier réellement)</p>
    <input type="file" accept="application/pdf" className="block mb-2" disabled />
    <button className="px-4 py-2 rounded bg-primary text-primary-foreground text-sm opacity-70 cursor-not-allowed">
      Mettre à jour CV (non-fonctionnel)
    </button>
  </section>
);
export default CVUploader;
