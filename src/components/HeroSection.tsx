import React from "react";
import CVDownloadButton from "./CVDownloadButton";
import { Link } from "react-router-dom";

const HeroSection = () => {
  return (
    <section className="relative w-full py-20 bg-gradient-to-b from-background to-muted animate-fade-in">
      <h1 className="text-5xl font-extrabold mb-4 bg-gradient-to-r from-primary to-primary/70 text-transparent bg-clip-text">
        Bonjour, je suis <span className="text-primary">[Votre nom]</span>
      </h1>
      <p className="max-w-2xl text-lg md:text-xl text-muted-foreground mb-8 text-center">
        Développeur passionné, créateur de solutions innovantes. Découvrez mes compétences et mes projets !
      </p>
      <div className="flex gap-4">
        <CVDownloadButton />
        <Link to="/projects" className="bg-primary text-primary-foreground font-medium rounded-lg px-6 py-3 hover:bg-primary/90 transition-all">Voir mes projets</Link>
      </div>
    </section>
  );
};

export default HeroSection;
