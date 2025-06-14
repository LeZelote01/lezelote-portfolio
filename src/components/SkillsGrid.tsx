import React from "react";
import { FileText } from "lucide-react";

const skills = [
  { name: "JavaScript", level: "Avancé", icon: FileText },
  { name: "React", level: "Avancé", icon: FileText },
  { name: "TypeScript", level: "Intermédiaire", icon: FileText },
  { name: "Node.js", level: "Intermédiaire", icon: FileText },
  { name: "Tailwind CSS", level: "Avancé", icon: FileText },
  { name: "Gestion de projet", level: "Avancé", icon: FileText },
];

const SkillsGrid = () => {
  return (
    <section className="max-w-5xl mx-auto py-16 animate-fade-in">
      <h2 className="text-3xl font-bold mb-8 text-primary">Compétences</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
        {skills.map(({ name, level, icon: Icon }) => (
          <div key={name} className="flex items-center bg-card rounded-lg shadow px-6 py-5 gap-4 border hover:shadow-lg transition-all">
            <Icon size={28} className="text-primary" />
            <div>
              <div className="font-semibold text-lg">{name}</div>
              <div className="text-xs text-muted-foreground">{level}</div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default SkillsGrid;
