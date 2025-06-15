
import React from "react";
import { FileText } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useTranslation } from "react-i18next";

const fetchSkills = async () => {
  const { data, error } = await supabase
    .from("skills")
    .select("id, name, name_en, level")
    .order("created_at", { ascending: true });
  if (error) throw new Error(error.message);
  return data || [];
};

const SkillsGrid = () => {
  const { t, i18n } = useTranslation();
  const { data: skills, isLoading, error } = useQuery({
    queryKey: ["skills"],
    queryFn: fetchSkills,
  });

  const filteredSkills = React.useMemo(() => skills ?? [], [skills]);

  return (
    <section className="max-w-5xl mx-auto py-10 sm:py-16 animate-fade-in px-2 sm:px-0">
      <h2 className="text-2xl sm:text-3xl font-bold mb-6 sm:mb-8 text-primary text-center">
        {i18n.language === "fr" ? "Compétences" : "Skills"}
      </h2>
      {isLoading && <div>{i18n.language === "fr" ? "Chargement…" : "Loading..."}</div>}
      {error && (
        <div className="text-red-500">
          {i18n.language === "fr"
            ? `Erreur de chargement : ${error.message}`
            : `Loading error: ${error.message}`}
        </div>
      )}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 sm:gap-8">
        {filteredSkills?.length ? (
          filteredSkills.map(({ id, name, name_en, level }) => (
            <div key={id} className="flex items-center bg-card rounded-lg shadow px-4 sm:px-6 py-4 sm:py-5 gap-4 border hover:shadow-lg transition-all">
              <FileText size={24} className="text-primary" />
              <div>
                <div className="font-semibold text-base sm:text-lg">
                  {i18n.language === "fr"
                    ? name
                    : name_en || name
                  }
                </div>
                <div className="text-xs text-muted-foreground">{level}</div>
              </div>
            </div>
          ))
        ) : !isLoading ? (
          <div className="col-span-full text-muted-foreground">
            {i18n.language === "fr"
              ? "Aucune compétence enregistrée."
              : "No skills found."}
          </div>
        ) : null}
      </div>
    </section>
  );
};

export default SkillsGrid;
