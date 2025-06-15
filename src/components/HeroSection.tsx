
import React from "react";
import CVDownloadButton from "./CVDownloadButton";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

const HeroSection = () => {
  const { t, i18n } = useTranslation();

  return (
    <section className="relative w-full min-h-[60vh] flex flex-col items-center justify-center gap-8 py-8 sm:py-20 bg-gradient-to-br from-primary/10 via-purple-100 to-indigo-100 dark:from-primary/30 dark:via-primary/10 dark:to-background animate-fade-in px-2 sm:px-0">
      <div className="absolute top-[-80px] left-4 w-28 h-28 rounded-full bg-indigo-400/20 blur-2xl z-0 animate-pulse hidden md:block"/>
      <div className="absolute right-4 bottom-[-80px] w-28 h-28 rounded-full bg-purple-400/15 blur-2xl z-0 animate-pulse hidden md:block"/>
      <h1 className="relative z-10 text-2xl xs:text-3xl md:text-5xl font-extrabold mb-2 text-center bg-gradient-to-r from-primary to-fuchsia-700 via-indigo-600 text-transparent bg-clip-text leading-tight">
        {t("hero.greeting")}
      </h1>
      {/* Courte phrase d'accroche complémentaire */}
      <div className="relative z-10 max-w-xl mx-auto text-center text-base sm:text-lg text-muted-foreground">
        {i18n.language === "fr"
          ? <>Bienvenue sur mon portfolio professionnel dédié à la cybersécurité, au développement Python, ainsi qu’à l’analyse réseau et à l’automatisation&nbsp;!</>
          : <>Welcome to my professional portfolio focused on cybersecurity, Python development, network analysis, and automation!</>}
      </div>
      <h2 className="relative z-10 text-primary text-base md:text-2xl font-semibold mb-0 text-center">{t("hero.subtitle")}</h2>
      <p className="relative z-10 max-w-xs xs:max-w-sm sm:max-w-2xl text-base md:text-xl text-muted-foreground mb-1 text-center drop-shadow-lg">
        {t("hero.paragraph1")}
      </p>
      <p className="relative z-10 max-w-xs xs:max-w-sm sm:max-w-2xl text-base md:text-lg text-muted-foreground mb-2 text-center drop-shadow-lg">
        {t("hero.paragraph2")}
      </p>
      <ul className="relative z-10 flex flex-col justify-center items-center gap-1 text-sm md:text-base text-muted-foreground">
        <li className="font-semibold">{t("hero.listTitle")}</li>
        <li>{t("hero.item1")}</li>
        <li>{t("hero.item2")}</li>
        <li>{t("hero.item3")}</li>
        <li>{t("hero.item4")}</li>
      </ul>
      <div className="relative z-10 flex flex-col xs:flex-row gap-3 xs:gap-4 mt-2 w-full justify-center items-center">
        <CVDownloadButton />
        <Link
          to="/projects"
          className="bg-gradient-to-r from-fuchsia-600 via-indigo-500 to-purple-400 text-white rounded px-5 py-2 hover:brightness-110 hover:from-purple-700 transition-all font-semibold shadow-md border-0"
        >
          {t("hero.cta_projects")}
        </Link>
      </div>
    </section>
  );
};

export default HeroSection;
