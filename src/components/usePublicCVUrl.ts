
import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";

export default function usePublicCVUrl() {
  const [cvUrl, setCvUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchCVUrl() {
      setLoading(true);
      // Utiliser le nom de fichier standardisé
      const { data } = supabase.storage.from("cv").getPublicUrl("lezelote-CV.pdf");
      if (data && data.publicUrl && data.publicUrl.endsWith(".pdf")) {
        setCvUrl(data.publicUrl);
      } else {
        setCvUrl(null);
      }
      setLoading(false);
    }
    fetchCVUrl();
  }, []);

  return { cvUrl, loading };
}
