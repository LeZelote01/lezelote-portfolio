
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import ContactForm from "@/components/ContactForm";
import { Helmet } from "react-helmet";

const Contact = () => (
  <>
    <Helmet>
      <title>Portfolio | Contact</title>
      <meta name="description" content="Formulaire de contact sécurisé pour échanger sur vos projets ou besoins." />
    </Helmet>
    <Navbar />
    <main className="py-20">
      <ContactForm />
    </main>
    <Footer />
  </>
);
export default Contact;
