
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import HeroSection from "@/components/HeroSection";
import SkillsGrid from "@/components/SkillsGrid";
import ProjectGallery from "@/components/ProjectGallery";
import { Helmet } from "react-helmet";
import AboutCard from "@/components/AboutCard";
import { useTranslation } from "react-i18next";

const Index = () => {
  const { t, i18n } = useTranslation();
  return (
    <>
      <Helmet>
        <title>Portfolio | Accueil</title>
        <meta name="description" content="Portfolio professionnel moderne : projets, compétences, contact et plus encore." />
      </Helmet>
      <Navbar />
      <main className="flex flex-col min-h-[90vh] justify-center items-center space-y-6 px-2">
        <HeroSection />
        {/* Nouvelle section de présentation */}
        <div className="max-w-2xl mx-auto text-center mt-2 mb-4 text-lg text-muted-foreground animate-fade-in">
          {i18n.language === "fr" ? (
            <>
              Bienvenue sur mon portfolio professionnel. Vous y trouverez mes principales compétences en cybersécurité, mes projets open-source, ainsi que mon parcours et ma passion pour les défis technologiques.
            </>
          ) : (
            <>
              Welcome to my professional portfolio. Here you’ll find my key skills in cybersecurity, open-source projects, my background, and my passion for technological challenges.
            </>
          )}
        </div>
        {/* Ajout de la carte À propos */}
        <AboutCard />
        <SkillsGrid />
        <ProjectGallery />
      </main>
      <Footer />
    </>
  );
};

export default Index;

