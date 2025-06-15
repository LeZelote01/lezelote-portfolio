
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { ExternalLink, Github, PlayCircle } from "lucide-react";

const fetchProjects = async () => {
  const { data, error } = await supabase
    .from("projects")
    .select("id, title, description, image_url, link, demo_url, github_url")
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
      <h2 className="text-2xl sm:text-3xl font-bold text-center mb-6 sm:mb-8">
        Projets Réalisés
      </h2>
      {isLoading && <div>Chargement…</div>}
      {error && <div className="text-red-500">Erreur de chargement : {error.message}</div>}
      <div className="grid grid-cols-1 gap-7 md:grid-cols-2 lg:grid-cols-3">
        {projects?.length ? (
          projects.map(
            ({
              id,
              title,
              description,
              image_url,
              link,
              demo_url,
              github_url,
            }) => (
              <div
                key={id}
                className="bg-white dark:bg-card rounded-2xl shadow-lg overflow-hidden flex flex-col h-full transition-transform hover:scale-[1.025] border border-muted "
              >
                <div className="relative">
                  <img
                    src={image_url || "https://via.placeholder.com/600x400"}
                    alt={title}
                    className="w-full h-44 sm:h-52 object-cover transition-all"
                  />
                  {demo_url && (
                    <span className="absolute top-3 left-3 bg-primary text-primary-foreground px-3 py-1 rounded-full text-xs shadow-lg flex items-center gap-1 font-semibold">
                      <PlayCircle size={16} />
                      Démo
                    </span>
                  )}
                </div>
                <div className="p-5 flex flex-col flex-1">
                  <h3 className="text-lg sm:text-xl font-semibold mb-1 sm:mb-2 flex gap-2 items-center">
                    {title}
                  </h3>
                  <p className="text-gray-700 dark:text-muted-foreground flex-1 mb-5">
                    {description || "—"}
                  </p>
                  <div className="mt-auto flex gap-3">
                    {demo_url && (
                      <a
                        href={demo_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white font-semibold px-3 py-1.5 rounded-full transition-all text-sm shadow"
                      >
                        <PlayCircle size={18} /> Démo
                      </a>
                    )}
                    {github_url && (
                      <a
                        href={github_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 bg-gray-900 hover:bg-gray-800 text-white font-semibold px-3 py-1.5 rounded-full transition-all text-sm shadow"
                      >
                        <Github size={18} /> GitHub
                      </a>
                    )}
                    {link && (
                      <a
                        href={link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 bg-primary text-primary-foreground hover:bg-primary/80 font-semibold px-3 py-1.5 rounded-full transition-all text-sm shadow"
                      >
                        <ExternalLink size={17} /> Voir
                      </a>
                    )}
                  </div>
                </div>
              </div>
            )
          )
        ) : !isLoading ? (
          <div className="col-span-full text-muted-foreground">
            Aucun projet enregistré.
          </div>
        ) : null}
      </div>
    </section>
  );
};

export default ProjectGallery;

