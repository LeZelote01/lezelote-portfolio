
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import ProjectGallery from "@/components/ProjectGallery";
import { Helmet } from "react-helmet";

const Projects = () => (
  <>
    <Helmet>
      <title>Portfolio | Projets</title>
      <meta name="description" content="Découvrez la galerie des projets réalisés et en cours." />
    </Helmet>
    <Navbar />
    <main>
      <ProjectGallery />
    </main>
    <Footer />
  </>
);

export default Projects;
