
import React from "react";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";
import usePublicCVUrl from "./usePublicCVUrl";

const CVDownloadButton = () => {
  const { cvUrl, loading } = usePublicCVUrl();

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
    <a
      href={cvUrl}
      download
      className="bg-gradient-to-r from-fuchsia-600 via-indigo-500 to-purple-400 text-white rounded px-5 py-2 hover:brightness-110 hover:from-purple-700 transition-all font-semibold shadow-md border-0 flex items-center gap-2"
      title="Télécharger mon CV"
    >
      <Download size={20} /> Télécharger CV
    </a>
  );
};

export default CVDownloadButton;
