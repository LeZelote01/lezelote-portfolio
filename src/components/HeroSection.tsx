
import React from "react";
import CVDownloadButton from "./CVDownloadButton";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

const HeroSection = () => {
  const { t, i18n } = useTranslation();

  return (
    <section className="relative w-full min-h-[60vh] flex flex-col items-center justify-center gap-6 py-8 sm:py-20 bg-gradient-to-br from-primary/10 via-purple-100 to-indigo-100 dark:from-primary/30 dark:via-primary/10 dark:to-background animate-fade-in px-2 sm:px-0">
      <div className="absolute top-[-80px] left-4 w-28 h-28 rounded-full bg-indigo-400/20 blur-2xl z-0 animate-pulse hidden md:block"/>
      <div className="absolute right-4 bottom-[-80px] w-28 h-28 rounded-full bg-purple-400/15 blur-2xl z-0 animate-pulse hidden md:block"/>
      <div className="relative z-10 w-full max-w-xl mx-auto text-center space-y-2">
        <h1 className="text-2xl xs:text-3xl md:text-5xl font-extrabold mb-0 text-center bg-gradient-to-r from-primary to-fuchsia-700 via-indigo-600 text-transparent bg-clip-text leading-tight">
          Jean Yves (LeZelote)
        </h1>
        <h2 className="text-primary text-base md:text-2xl font-semibold mb-1 mt-1 text-center">{t("hero.subtitle")}</h2>
        <div className="flex flex-col gap-1">
          <p className="max-w-xs xs:max-w-sm sm:max-w-2xl text-base md:text-xl text-muted-foreground text-center drop-shadow-lg">
            {t("hero.paragraph1")}
          </p>
          <p className="max-w-xs xs:max-w-sm sm:max-w-2xl text-base md:text-lg text-muted-foreground text-center drop-shadow-lg">
            {t("hero.paragraph2")}
          </p>
        </div>
        <ul className="flex flex-col justify-center items-center gap-1 text-sm md:text-base text-muted-foreground mt-2">
          <li className="font-semibold">{t("hero.listTitle")}</li>
          <li>{t("hero.item1")}</li>
          <li>{t("hero.item2")}</li>
          <li>{t("hero.item3")}</li>
          <li>{t("hero.item4")}</li>
        </ul>
        {/* Bloc d’accroche principal juste avant les boutons */}
        <div className="mt-4 mb-0 text-base sm:text-lg text-muted-foreground">
          {i18n.language === "fr"
            ? (
              <>
                Parcourez mes principales compétences en cybersécurité, mes réalisations open-source, ainsi que mon parcours orienté vers la sécurité offensive, le développement Python et l'automatisation. Explorez mes projets, découvrez mon approche de l'analyse réseau, et n'hésitez pas à me contacter pour toute collaboration ou question technique : passionné par les défis technologiques, je mets mon expertise au service de la sécurité numérique !
              </>
            ) : (
              <>
                Discover my key skills in cybersecurity, my open-source achievements, and my background focused on offensive security, Python development, and automation. Browse my projects, learn about my approach to network analysis, and feel free to reach out for any collaboration or technical question. Passionate about technological challenges, I put my expertise at the service of digital security!
              </>
            )
          }
        </div>
      </div>
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
