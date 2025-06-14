
import { useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";

const CVUploader = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files?.[0] ?? null);
    setSuccess(null);
    setError(null);
  };

  const uploadCV = async () => {
    setUploading(true);
    setSuccess(null);
    setError(null);
    if (!file) {
      setError("Aucun fichier sélectionné.");
      setUploading(false);
      return;
    }
    try {
      // Always save as 'cv.pdf' and overwrite
      const { error: uploadError } = await supabase.storage.from("cv").upload("cv.pdf", file, {
        cacheControl: "3600",
        upsert: true,
        contentType: "application/pdf",
      });
      if (uploadError) throw uploadError;
      setSuccess("CV mis en ligne !");
      setFile(null);
    } catch (err: any) {
      setError(err.message || "Erreur lors de l'upload.");
    }
    setUploading(false);
  };

  return (
    <section className="bg-card rounded-lg shadow p-6 border">
      <h2 className="font-bold text-lg mb-2">Télécharger/Mettre à jour le CV</h2>
      <input
        type="file"
        accept="application/pdf"
        className="block mb-2"
        onChange={handleFileChange}
        disabled={uploading}
      />
      <Button
        onClick={uploadCV}
        className="mb-2"
        disabled={!file || uploading}
      >
        {uploading ? "Téléchargement…" : "Mettre à jour CV"}
      </Button>
      {success && <div className="text-green-600 text-sm">{success}</div>}
      {error && <div className="text-red-600 text-sm">{error}</div>}

      <hr className="my-3" />
      <a
        href={`${import.meta.env.BASE_URL ?? "/"}storage/v1/object/public/cv/cv.pdf`}
        target="_blank"
        rel="noopener noreferrer"
        className="underline text-primary"
      >
        Voir le CV actuel (pdf)
      </a>
    </section>
  );
};
export default CVUploader;
