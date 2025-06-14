
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import SkillsGrid from "@/components/SkillsGrid";
import { Helmet } from "react-helmet";

const Skills = () => (
  <>
    <Helmet>
      <title>Portfolio | Compétences</title>
      <meta name="description" content="Découvrez mes compétences professionnelles dans le développement et d'autres domaines." />
    </Helmet>
    <Navbar />
    <main>
      <SkillsGrid />
    </main>
    <Footer />
  </>
);
export default Skills;
