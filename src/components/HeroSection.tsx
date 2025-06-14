
import React from "react";
import CVDownloadButton from "./CVDownloadButton";
import { Link } from "react-router-dom";

const HeroSection = () => {
  return (
    <section className="relative w-full min-h-[60vh] flex flex-col items-center justify-center gap-8 py-8 sm:py-20 bg-gradient-to-br from-primary/10 via-purple-100 to-indigo-100 dark:from-primary/30 dark:via-primary/10 dark:to-background animate-fade-in px-2 sm:px-0">
      <div className="absolute top-[-80px] left-4 w-28 h-28 rounded-full bg-indigo-400/20 blur-2xl z-0 animate-pulse hidden md:block"/>
      <div className="absolute right-4 bottom-[-80px] w-28 h-28 rounded-full bg-purple-400/15 blur-2xl z-0 animate-pulse hidden md:block"/>
      <h1 className="relative z-10 text-2xl xs:text-3xl md:text-5xl font-extrabold mb-2 text-center bg-gradient-to-r from-primary to-fuchsia-700 via-indigo-600 text-transparent bg-clip-text leading-tight">
        Bonjour, je suis <span className="text-fuchsia-600 dark:text-sky-400">[Votre nom]</span>
      </h1>
      <p className="relative z-10 max-w-xs xs:max-w-sm sm:max-w-2xl text-base md:text-xl text-muted-foreground mb-3 md:mb-6 text-center drop-shadow-lg">
        Développeur passionné, créateur de <span className="bg-clip-text text-transparent bg-gradient-to-r from-fuchsia-500 via-pink-500 to-indigo-500">solutions innovantes</span>.
        <br className="hidden xs:block" />
        Découvrez mes compétences et mes projets !
      </p>
      <div className="relative z-10 flex flex-col xs:flex-row gap-3 xs:gap-4 mt-2 animate-fade-in w-full justify-center items-center">
        <CVDownloadButton />
        <Link
          to="/projects"
          className="bg-gradient-to-r from-fuchsia-600 via-indigo-500 to-purple-400 text-white rounded px-5 py-2 hover:brightness-110 hover:from-purple-700 transition-all font-semibold shadow-md border-0"
        >
          Voir mes projets
        </Link>
      </div>
    </section>
  );
};

export default HeroSection;
