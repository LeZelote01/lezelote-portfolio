
import React from "react";
import CVDownloadButton from "./CVDownloadButton";
import { Link } from "react-router-dom";

const HeroSection = () => {
  return (
    <section className="relative w-full min-h-[65vh] flex flex-col items-center justify-center gap-8 py-12 sm:py-20 bg-gradient-to-br from-primary/10 via-purple-100 to-indigo-100 dark:from-primary/30 dark:via-primary/10 dark:to-background animate-fade-in">
      <div className="absolute top-[-80px] left-10 w-40 h-40 rounded-full bg-indigo-400/20 blur-2xl z-0 animate-pulse hidden md:block"/>
      <div className="absolute right-10 bottom-[-80px] w-40 h-40 rounded-full bg-purple-400/15 blur-2xl z-0 animate-pulse hidden md:block"/>

      <h1 className="relative z-10 text-4xl md:text-5xl font-extrabold mb-2 text-center bg-gradient-to-r from-primary to-fuchsia-700 via-indigo-600 text-transparent bg-clip-text">
        Bonjour, je suis <span className="text-fuchsia-600 dark:text-sky-400">[Votre nom]</span>
      </h1>
      <p className="relative z-10 max-w-2xl text-base md:text-xl text-muted-foreground mb-3 md:mb-6 text-center drop-shadow-lg">
        Développeur passionné, créateur de <span className="bg-clip-text text-transparent bg-gradient-to-r from-fuchsia-500 via-pink-500 to-indigo-500">solutions innovantes</span>.
        <br />
        Découvrez mes compétences et mes projets !
      </p>
      <div className="relative z-10 flex gap-4 mt-2 animate-fade-in">
        <CVDownloadButton />
        <Link
          to="/projects"
          className="bg-gradient-to-r from-indigo-500 to-fuchsia-500 text-white font-semibold rounded-lg px-6 py-3 shadow-md hover:scale-105 hover:from-fuchsia-500 hover:to-pink-400 transition-all duration-200"
        >
          Voir mes projets
        </Link>
      </div>
    </section>
  );
};

export default HeroSection;
