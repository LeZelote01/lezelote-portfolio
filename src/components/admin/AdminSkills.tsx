
import { useSkillsAdmin } from "@/hooks/useSkillsAdmin";
import { useState } from "react";
import { Pencil, Plus, Trash2, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const LEVELS = ["Débutant", "Intermédiaire", "Avancé", "Expert"];

const AdminSkills = () => {
  const { data: skills = [], isLoading, error, create, update, remove } = useSkillsAdmin();
  const [adding, setAdding] = useState(false);
  const [editing, setEditing] = useState<string | null>(null);
  const [form, setForm] = useState({ name: "", level: LEVELS[0] });

  // Reset form when closing modal
  const resetForm = () => {
    setForm({ name: "", level: LEVELS[0] });
    setAdding(false);
    setEditing(null);
  };

  // Handle edit click
  const handleEdit = (skill: any) => {
    setForm({ name: skill.name, level: skill.level });
    setEditing(skill.id);
    setAdding(false);
  };

  return (
    <section className="bg-card rounded-lg shadow p-6 border">
      <h2 className="font-bold text-lg mb-2">Gérer les compétences</h2>
      {isLoading && <div>Chargement…</div>}
      {error && <div className="text-red-500">{error.message}</div>}
      <ul className="space-y-2 mb-4">
        {skills.map(skill => (
          <li key={skill.id} className="flex items-center gap-2">
            <span className="flex-1 font-semibold">{skill.name}</span>
            <span className="text-xs text-muted-foreground mr-2">{skill.level}</span>
            <Button size="icon" variant="ghost" onClick={() => handleEdit(skill)} aria-label="Modifier">
              <Pencil size={16} />
            </Button>
            <Button size="icon" variant="ghost" onClick={() => remove.mutate(skill.id)} aria-label="Supprimer" className="text-destructive" disabled={remove.isPending}>
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
                { id: editing, name: form.name, level: form.level },
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
            value={form.name}
            onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
            placeholder="Nom de la compétence"
            required
            autoFocus
          />
          <select
            className="w-full border rounded px-2 py-1"
            value={form.level}
            onChange={e => setForm(f => ({ ...f, level: e.target.value }))}
          >
            {LEVELS.map(level => <option key={level}>{level}</option>)}
          </select>
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
          onClick={() => { setAdding(true); setEditing(null); setForm({ name: "", level: LEVELS[0] }); }}
        >
          <Plus size={16} className="mr-1 -ml-1" />
          Ajouter une compétence
        </Button>
      )}
    </section>
  );
};
export default AdminSkills;
