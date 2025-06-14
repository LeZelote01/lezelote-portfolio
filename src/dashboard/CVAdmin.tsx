
import { useRef, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";

const BUCKET = "cv";
const OBJECT_KEY = "public-cv.pdf";

const CVAdmin = () => {
  const fileInput = useRef<HTMLInputElement | null>(null);
  const [uploading, setUploading] = useState(false);
  const [cvUrl, setCvUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Get URL of the current CV (if exists)
  const fetchCV = async () => {
    const { data } = supabase.storage.from(BUCKET).getPublicUrl(OBJECT_KEY);
    setCvUrl(data?.publicUrl || null);
  };

  // Upload new CV (overwrite)
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
    if (error) setError("Erreur à l'upload du fichier.");
    else fetchCV();
  };

  // Supprimer le CV
  const handleDelete = async () => {
    setUploading(true);
    setError(null);
    await supabase.storage.from(BUCKET).remove([OBJECT_KEY]);
    setUploading(false);
    fetchCV();
  };

  // fetch CV on mount
  if (cvUrl === null) fetchCV();

  return (
    <section className="max-w-3xl mx-auto bg-white dark:bg-fuchsia-900 p-6 rounded-lg shadow mt-6">
      <h2 className="text-xl font-bold mb-4">Ajouter ou remplacer le CV (PDF)</h2>
      {cvUrl && (
        <div className="mb-4">
          <a href={cvUrl} target="_blank" rel="noopener" className="text-primary underline">Voir le CV actuel</a>
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
  );
};
export default CVAdmin;
