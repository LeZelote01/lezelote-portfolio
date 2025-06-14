
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
    <section className="max-w-5xl mx-auto py-16 animate-fade-in">
      <h2 className="text-3xl font-bold text-center mb-8">Projets Réalisés</h2>
      {isLoading && <div>Chargement…</div>}
      {error && <div className="text-red-500">Erreur de chargement : {error.message}</div>}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects?.length ? (
          projects.map(({ id, title, description, image_url, link }) => (
            <div key={id} className="bg-white rounded-lg shadow-md overflow-hidden">
              <img
                src={image_url || "https://via.placeholder.com/600x400"}
                alt={title}
                className="w-full h-48 object-cover"
              />
              <div className="p-4">
                <h3 className="text-xl font-semibold mb-2">{title}</h3>
                <p className="text-gray-700">{description || "—"}</p>
                {link && (
                  <a
                    href={link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block mt-4 bg-primary text-primary-foreground py-2 px-4 rounded hover:bg-primary/80 transition-colors"
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
