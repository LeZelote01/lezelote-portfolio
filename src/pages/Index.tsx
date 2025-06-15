
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import HeroSection from "@/components/HeroSection";
import SkillsGrid from "@/components/SkillsGrid";
import ProjectGallery from "@/components/ProjectGallery";
import { Helmet } from "react-helmet";
import { useTranslation } from "react-i18next";

const Index = () => {
  const { i18n } = useTranslation();
  return (
    <>
      <Helmet>
        <title>Portfolio | Accueil</title>
        <meta name="description" content="Portfolio professionnel moderne : projets, compétences, contact et plus encore." />
      </Helmet>
      <Navbar />
      <main className="flex flex-col min-h-[90vh] justify-center items-center space-y-6 px-2">
        <HeroSection />
        {/* Présentation fusionnée et cohérente */}
        <div className="max-w-2xl mx-auto text-center mt-2 mb-4 text-lg text-muted-foreground animate-fade-in">
          {i18n.language === "fr"
            ? (
              <>
                Parcourez mes principales compétences en cybersécurité, mes réalisations open-source, ainsi que mon parcours orienté vers la sécurité offensive, le développement Python et l'automatisation. Explorez mes projets, découvrez mon approche de l'analyse réseau, et n'hésitez pas à me contacter pour toute collaboration ou question technique : passionné par les défis technologiques, je mets mon expertise au service de la sécurité numérique&nbsp;!
              </>
            )
            : (
              <>
                Discover my key skills in cybersecurity, my open-source achievements, and my background focused on offensive security, Python development, and automation. Browse my projects, learn about my approach to network analysis, and feel free to reach out for any collaboration or technical question. Passionate about technological challenges, I put my expertise at the service of digital security!
              </>
            )
          }
        </div>
        <SkillsGrid />
        <ProjectGallery />
      </main>
      <Footer />
    </>
  );
};

export default Index;
