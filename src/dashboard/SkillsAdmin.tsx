
import { useSkillsAdmin } from "@/hooks/useSkillsAdmin";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Plus, Edit, Trash2 } from "lucide-react";
import DashboardLayout from "./DashboardLayout";

const EmptySkill = { name: "", name_en: "", level: "" };

const SkillsAdmin = () => {
  const { data, isLoading, error, create, update, remove } = useSkillsAdmin();
  const [editId, setEditId] = useState<string | null>(null);
  const [form, setForm] = useState({ ...EmptySkill });
  const [showForm, setShowForm] = useState(false);

  const handleEdit = (skill: any) => {
    setForm({ name: skill.name ?? "", name_en: skill.name_en ?? "", level: skill.level ?? "" });
    setEditId(skill.id);
    setShowForm(true);
  };

  const handleCreate = () => {
    setForm({ ...EmptySkill });
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
    setEditId(null);
    setForm({ ...EmptySkill });
  };

  return (
    <DashboardLayout>
      <section className="max-w-3xl mx-auto bg-white dark:bg-fuchsia-900 p-6 rounded-lg shadow mt-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">Gestion des Compétences</h2>
          <Button onClick={handleCreate} variant="default" size="sm"><Plus />Ajouter</Button>
        </div>
        {showForm && (
          <form className="space-y-4 mb-6" onSubmit={handleSubmit}>
            <input
              className="border rounded px-3 py-2 w-full"
              placeholder="Nom (français)"
              value={form.name}
              required
              onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
            />
            <input
              className="border rounded px-3 py-2 w-full"
              placeholder="Nom (anglais)"
              value={form.name_en}
              required
              onChange={e => setForm(f => ({ ...f, name_en: e.target.value }))}
            />
            <input
              className="border rounded px-3 py-2 w-full"
              placeholder="Niveau"
              value={form.level}
              required
              onChange={e => setForm(f => ({ ...f, level: e.target.value }))}
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
          {data?.map((s: any) => (
            <li key={s.id} className="flex items-center justify-between py-3">
              <div>
                <div className="font-medium">
                  {s.name} <span className="text-xs text-gray-400">/ {s.name_en}</span>
                </div>
                <div className="text-xs text-gray-500">{s.level}</div>
              </div>
              <div className="flex gap-2">
                <Button size="icon" variant="outline" onClick={() => handleEdit(s)}><Edit /></Button>
                <Button size="icon" variant="destructive" onClick={() => remove.mutate(s.id)}><Trash2 /></Button>
              </div>
            </li>
          ))}
        </ul>
      </section>
    </DashboardLayout>
  );
};

export default SkillsAdmin;
