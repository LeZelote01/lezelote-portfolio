import { useRef, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import DashboardLayout from "./DashboardLayout";

const BUCKET = "cv";
const OBJECT_KEY = "public-cv.pdf";

const CVAdmin = () => {
  const fileInput = useRef<HTMLInputElement | null>(null);
  const [uploading, setUploading] = useState(false);
  const [cvUrl, setCvUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Charger l'URL actuelle du CV public
  const fetchCV = async () => {
    const { data } = supabase.storage.from(BUCKET).getPublicUrl(OBJECT_KEY);
    if (data && data.publicUrl && data.publicUrl.endsWith('.pdf')) {
      setCvUrl(data.publicUrl);
      setError(null);
    } else {
      setCvUrl(null);
      setError("Aucun CV n'est actuellement disponible.");
    }
  };

  // Upload d'un nouveau CV (réservé admin RLS)
  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fileInput.current?.files?.[0]) return;
    setUploading(true);
    setError(null);
    const file = fileInput.current.files[0];
    const { error } = await supabase.storage.from(BUCKET).upload(OBJECT_KEY, file, {
      upsert: true,
      contentType: "application/pdf",
    });
    setUploading(false);
    if (error) {
      if (error.message.includes("Unauthorized")) {
        setError("Vous n'avez pas l'autorisation pour envoyer un CV (réservé aux admins).");
      } else {
        setError("Erreur à l'upload du fichier.");
      }
    } else {
      fetchCV();
    }
  };

  // Suppression du CV (réservé admin RLS)
  const handleDelete = async () => {
    setUploading(true);
    setError(null);
    const { error } = await supabase.storage.from(BUCKET).remove([OBJECT_KEY]);
    setUploading(false);
    if (error) {
      if (error.message.includes("Unauthorized")) {
        setError("Vous n'avez pas l'autorisation pour supprimer ce CV.");
      } else {
        setError("Erreur à la suppression du fichier.");
      }
    } else {
      fetchCV();
    }
  };

  // Chargement CV à l'ouverture
  if (cvUrl === null) fetchCV();

  return (
    <DashboardLayout>
      <section className="max-w-3xl mx-auto bg-white dark:bg-fuchsia-900 p-6 rounded-lg shadow mt-6">
        <h2 className="text-xl font-bold mb-4">Ajouter ou remplacer le CV (PDF sur le bucket cv)</h2>
        {cvUrl && (
          <div className="mb-4">
            <a href={cvUrl} target="_blank" rel="noopener" className="text-primary underline">
              Voir le CV actuel
            </a>
          </div>
        )}
        {error && <div className="text-red-500">{error}</div>}
        <form className="flex items-center gap-4 mb-6" onSubmit={handleUpload}>
          <input
            type="file"
            accept="application/pdf"
            ref={fileInput}
            className="block border p-2 rounded"
            required
            disabled={uploading}
          />
          <Button type="submit" variant="default" size="sm" disabled={uploading}>
            {uploading ? "Upload en cours…" : "Uploader le fichier"}
          </Button>
        </form>
        {cvUrl && (
          <Button variant="destructive" size="sm" onClick={handleDelete} disabled={uploading}>
            Supprimer le CV actuel
          </Button>
        )}
      </section>
    </DashboardLayout>
  );
};
export default CVAdmin;
