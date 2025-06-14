
import { useProjectsAdmin } from "@/hooks/useProjectsAdmin";
import { Plus, Edit, Trash2 } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";

const EmptyProject = { title: "", description: "", image_url: "", link: "" };

const ProjectsAdmin = () => {
  const { data, isLoading, error, create, update, remove } = useProjectsAdmin();
  const [editId, setEditId] = useState<string | null>(null);
  const [form, setForm] = useState({ ...EmptyProject });
  const [showForm, setShowForm] = useState(false);

  const handleEdit = (project: any) => {
    setForm({ title: project.title ?? "", description: project.description ?? "", image_url: project.image_url ?? "", link: project.link ?? "" });
    setEditId(project.id);
    setShowForm(true);
  };

  const handleCreate = () => {
    setForm({ ...EmptyProject });
    setEditId(null);
    setShowForm(true);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editId) {
      update.mutate({ id: editId, ...form });
    } else {
      create.mutate(form);
    }
    setShowForm(false);
    setForm({ ...EmptyProject });
    setEditId(null);
  };

  return (
    <section className="max-w-3xl mx-auto bg-white dark:bg-fuchsia-900 p-6 rounded-lg shadow mt-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">Gestion des Projets</h2>
        <Button onClick={handleCreate} variant="default" size="sm"><Plus />Ajouter</Button>
      </div>
      {showForm && (
        <form className="space-y-4 mb-6" onSubmit={handleSubmit}>
          <input
            className="border rounded px-3 py-2 w-full"
            placeholder="Titre"
            value={form.title}
            required
            onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
          />
          <textarea
            className="border rounded px-3 py-2 w-full"
            placeholder="Description"
            value={form.description}
            onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
          />
          <input
            className="border rounded px-3 py-2 w-full"
            placeholder="Image (URL)"
            value={form.image_url}
            onChange={e => setForm(f => ({ ...f, image_url: e.target.value }))}
          />
          <input
            className="border rounded px-3 py-2 w-full"
            placeholder="Lien du projet"
            value={form.link}
            onChange={e => setForm(f => ({ ...f, link: e.target.value }))}
          />
          <div className="flex gap-4">
            <Button type="submit" variant="default" size="sm">
              {editId ? <>Modifier</> : <>Créer</>}
            </Button>
            <Button type="button" variant="secondary" size="sm" onClick={() => setShowForm(false)}>Annuler</Button>
          </div>
        </form>
      )}
      {isLoading && <div>Chargement…</div>}
      {error && <div className="text-red-500">Erreur : {error.message}</div>}
      <ul className="divide-y">
        {data?.map((p: any) => (
          <li key={p.id} className="flex items-center justify-between py-3">
            <div>
              <div className="font-medium">{p.title}</div>
              <div className="text-xs text-gray-500">{p.description}</div>
            </div>
            <div className="flex gap-2">
              <Button size="icon" variant="outline" onClick={() => handleEdit(p)}><Edit /></Button>
              <Button size="icon" variant="destructive" onClick={() => remove.mutate(p.id)}><Trash2 /></Button>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
};

export default ProjectsAdmin;
