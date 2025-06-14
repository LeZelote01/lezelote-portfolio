
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

const fetchProjects = async () => {
  const { data, error } = await supabase
    .from("projects")
    .select("id, title, description, image_url, link")
    .order("created_at", { ascending: false });
  if (error) throw new Error(error.message);
  return data || [];
};

const ProjectGallery = () => {
  const { data: projects, isLoading, error } = useQuery({
    queryKey: ["projects"],
    queryFn: fetchProjects,
  });

  return (
    <section className="max-w-5xl mx-auto py-10 sm:py-16 animate-fade-in px-2 sm:px-0">
      <h2 className="text-2xl sm:text-3xl font-bold text-center mb-6 sm:mb-8">Projets Réalisés</h2>
      {isLoading && <div>Chargement…</div>}
      {error && <div className="text-red-500">Erreur de chargement : {error.message}</div>}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {projects?.length ? (
          projects.map(({ id, title, description, image_url, link }) => (
            <div key={id} className="bg-white rounded-lg shadow-md overflow-hidden flex flex-col h-full">
              <img
                src={image_url || "https://via.placeholder.com/600x400"}
                alt={title}
                className="w-full h-44 sm:h-48 object-cover"
              />
              <div className="p-4 flex flex-col flex-1">
                <h3 className="text-lg sm:text-xl font-semibold mb-1 sm:mb-2">{title}</h3>
                <p className="text-gray-700 flex-1">{description || "—"}</p>
                {link && (
                  <a
                    href={link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block mt-4 bg-primary text-primary-foreground py-2 px-4 rounded hover:bg-primary/80 transition-colors text-center w-full"
                  >
                    Voir le Projet
                  </a>
                )}
              </div>
            </div>
          ))
        ) : !isLoading ? (
          <div className="col-span-full text-muted-foreground">Aucun projet enregistré.</div>
        ) : null}
      </div>
    </section>
  );
};

export default ProjectGallery;
