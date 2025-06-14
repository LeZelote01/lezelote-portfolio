
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import AboutCard from "@/components/AboutCard";
import { Helmet } from "react-helmet";

const About = () => (
  <>
    <Helmet>
      <title>Portfolio | À propos</title>
      <meta name="description" content="En savoir plus sur mon parcours, mes expériences et mes passions." />
    </Helmet>
    <Navbar />
    <main>
      <AboutCard />
    </main>
    <Footer />
  </>
);

export default About;
