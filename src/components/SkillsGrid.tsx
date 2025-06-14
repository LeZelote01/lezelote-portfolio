
import React from "react";
import { FileText } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

const fetchSkills = async () => {
  const { data, error } = await supabase
    .from("skills")
    .select("id, name, level")
    .order("created_at", { ascending: true });
  if (error) throw new Error(error.message);
  return data || [];
};

const SkillsGrid = () => {
  const { data: skills, isLoading, error } = useQuery({
    queryKey: ["skills"],
    queryFn: fetchSkills,
  });

  return (
    <section className="max-w-5xl mx-auto py-10 sm:py-16 animate-fade-in px-2 sm:px-0">
      <h2 className="text-2xl sm:text-3xl font-bold mb-6 sm:mb-8 text-primary text-center">Compétences</h2>
      {isLoading && <div>Chargement…</div>}
      {error && <div className="text-red-500">Erreur de chargement : {error.message}</div>}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 sm:gap-8">
        {skills?.length ? (
          skills.map(({ id, name, level }) => (
            <div key={id} className="flex items-center bg-card rounded-lg shadow px-4 sm:px-6 py-4 sm:py-5 gap-4 border hover:shadow-lg transition-all">
              <FileText size={24} className="text-primary" />
              <div>
                <div className="font-semibold text-base sm:text-lg">{name}</div>
                <div className="text-xs text-muted-foreground">{level}</div>
              </div>
            </div>
          ))
        ) : !isLoading ? (
          <div className="col-span-full text-muted-foreground">Aucune compétence enregistrée.</div>
        ) : null}
      </div>
    </section>
  );
};

export default SkillsGrid;
