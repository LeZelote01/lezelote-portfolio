
import { useProjectsAdmin } from "@/hooks/useProjectsAdmin";
import { useState } from "react";
import { Pencil, Plus, Trash2, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const AdminProjects = () => {
  const { data: projects = [], isLoading, error, create, update, remove } = useProjectsAdmin();
  const [adding, setAdding] = useState(false);
  const [editing, setEditing] = useState<string | null>(null);
  const [form, setForm] = useState({ title: "", description: "", image_url: "", link: "" });

  // Reset form
  const resetForm = () => {
    setForm({ title: "", description: "", image_url: "", link: "" });
    setAdding(false);
    setEditing(null);
  };

  // Handle edit click
  const handleEdit = (p: any) => {
    setForm({
      title: p.title ?? "",
      description: p.description ?? "",
      image_url: p.image_url ?? "",
      link: p.link ?? "",
    });
    setEditing(p.id);
    setAdding(false);
  };

  return (
    <section className="bg-card rounded-lg shadow p-6 border">
      <h2 className="font-bold text-lg mb-2">Gérer les projets</h2>
      {isLoading && <div>Chargement…</div>}
      {error && <div className="text-red-500">{error.message}</div>}
      <ul className="space-y-2 mb-4">
        {projects.map(project => (
          <li key={project.id} className="flex flex-col gap-0.5 sm:flex-row sm:items-center sm:gap-2">
            <span className="font-semibold flex-1">{project.title}</span>
            <span className="text-xs text-muted-foreground">{project.description}</span>
            <Button size="icon" variant="ghost" onClick={() => handleEdit(project)} aria-label="Éditer">
              <Pencil size={16} />
            </Button>
            <Button size="icon" variant="ghost" onClick={() => remove.mutate(project.id)} aria-label="Supprimer" className="text-destructive" disabled={remove.isPending}>
              <Trash2 size={16} />
            </Button>
          </li>
        ))}
      </ul>
      {/* Add/Edit Form */}
      {(adding || editing) && (
        <form
          onSubmit={e => {
            e.preventDefault();
            if (editing)
              update.mutate(
                { id: editing, ...form },
                { onSuccess: resetForm }
              );
            else
              create.mutate(
                { ...form },
                { onSuccess: resetForm }
              );
          }}
          className="space-y-2 mb-2"
        >
          <Input
            value={form.title}
            onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
            placeholder="Titre"
            required
            autoFocus
          />
          <Input
            value={form.description}
            onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
            placeholder="Description"
          />
          <Input
            value={form.image_url}
            onChange={e => setForm(f => ({ ...f, image_url: e.target.value }))}
            placeholder="Image URL"
          />
          <Input
            value={form.link}
            onChange={e => setForm(f => ({ ...f, link: e.target.value }))}
            placeholder="Lien (optionnel)"
          />
          <div className="flex gap-2">
            <Button type="submit" disabled={create.isPending || update.isPending}>
              {editing ? "Enregistrer" : "Ajouter"}
            </Button>
            <Button type="button" variant="outline" onClick={resetForm}>
              <X size={16} className="mr-1 -ml-1" /> Annuler
            </Button>
          </div>
        </form>
      )}
      {!adding && !editing && (
        <Button
          className="mt-2"
          onClick={() => { setAdding(true); setEditing(null); setForm({ title: "", description: "", image_url: "", link: "" }); }}
        >
          <Plus size={16} className="mr-1 -ml-1" />
          Ajouter un projet
        </Button>
      )}
    </section>
  );
};
export default AdminProjects;
