
import { Image } from "lucide-react";
const projects = [
  {
    title: "Super projet SaaS",
    description: "Application SaaS robuste permettant la gestion efficace des tâches.",
    img: "/photo-1488590528505-98d2b5aba04b",
    tags: ["React", "API", "SaaS"],
    url: "#"
  },
  {
    title: "Portfolio interactif",
    description: "Un portfolio dynamique optimisé pour mobile et desktop.",
    img: "/photo-1486312338219-ce68d2c6f44d",
    tags: ["Responsive", "UI/UX", "Vite"],
    url: "#"
  },
  {
    title: "Dashboard CRM",
    description: "Un tableau de bord moderne pour le suivi de clients.",
    img: "/photo-1461749280684-dccba630e2f6",
    tags: ["Dashboard", "CRM", "Analytique"],
    url: "#"
  },
];

const ProjectGallery = () => (
  <section className="max-w-6xl mx-auto py-16 px-4">
    <h2 className="text-3xl font-bold mb-8 text-primary">Mes Projets</h2>
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
      {projects.map(({ title, description, img, tags, url }) => (
        <a
          key={title}
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="block bg-card rounded-lg border shadow hover:shadow-xl transition-all"
        >
          <div className="aspect-video bg-muted rounded-t-lg overflow-hidden">
            {img ? (
              <img src={img} alt={title} className="object-cover w-full h-full" />
            ) : (
              <div className="flex flex-col items-center justify-center h-full">
                <Image className="text-muted-foreground" size={40} />
              </div>
            )}
          </div>
          <div className="p-5">
            <h3 className="font-semibold text-xl mb-1">{title}</h3>
            <p className="text-muted-foreground text-sm mb-2">{description}</p>
            <div className="flex flex-wrap gap-1">
              {tags.map(tag => (
                <span
                  key={tag}
                  className="text-xs px-2 py-0.5 rounded bg-primary/10 text-primary font-semibold"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </a>
      ))}
    </div>
  </section>
);
export default ProjectGallery;
