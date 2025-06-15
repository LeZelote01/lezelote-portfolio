
import React from "react";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";
import usePublicCVUrl from "./usePublicCVUrl";

const CV_FILENAME = "lezelote-CV.pdf";

const CVDownloadButton = () => {
  const { cvUrl, loading } = usePublicCVUrl();

  // Téléchargement forcé avec fetch et Blob
  const handleDownload = async () => {
    if (!cvUrl) return;
    try {
      const response = await fetch(cvUrl);
      if (!response.ok) {
        throw new Error("Erreur lors du chargement du fichier");
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = url;
      link.download = CV_FILENAME; // Nom du fichier téléchargé
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      setTimeout(() => window.URL.revokeObjectURL(url), 200);
    } catch (error) {
      alert("Le téléchargement du CV a échoué.");
    }
  };

  if (loading) {
    return (
      <Button
        disabled
        className="bg-gradient-to-r from-fuchsia-600 via-indigo-500 to-purple-400 text-white rounded px-5 py-2 font-semibold shadow-md border-0 animate-pulse"
      >
        Chargement du CV…
      </Button>
    );
  }
  if (!cvUrl) {
    return (
      <Button
        disabled
        variant="secondary"
        className="rounded px-5 py-2 font-semibold border-0 opacity-70"
        title="Aucun CV disponible"
      >
        CV indisponible
      </Button>
    );
  }

  return (
    <Button
      onClick={handleDownload}
      className="bg-gradient-to-r from-fuchsia-600 via-indigo-500 to-purple-400 text-white rounded px-5 py-2 hover:brightness-110 hover:from-purple-700 transition-all font-semibold shadow-md border-0 flex items-center gap-2"
      title="Télécharger mon CV"
    >
      <Download size={20} /> Télécharger CV
    </Button>
  );
};

export default CVDownloadButton;

