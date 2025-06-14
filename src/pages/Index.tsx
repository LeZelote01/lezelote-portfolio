
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import HeroSection from "@/components/HeroSection";
import SkillsGrid from "@/components/SkillsGrid";
import ProjectGallery from "@/components/ProjectGallery";
import { Helmet } from "react-helmet";

const Index = () => {
  return (
    <>
      <Helmet>
        <title>Portfolio | Accueil</title>
        <meta name="description" content="Portfolio professionnel moderne : projets, compétences, contact et plus encore." />
      </Helmet>
      <Navbar />
      <main>
        <HeroSection />
        <SkillsGrid />
        <ProjectGallery />
      </main>
      <Footer />
    </>
  );
};

export default Index;
