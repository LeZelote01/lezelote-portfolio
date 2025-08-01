import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "./context/ThemeContext.jsx";
import { LanguageProvider } from "./context/LanguageContext.jsx";
import Layout from "./components/Layout.jsx";
import Home from "./pages/Home.jsx";
import About from "./pages/About.jsx";
import Skills from "./pages/Skills.jsx";
import Projects from "./pages/Projects.jsx";
import Services from "./pages/Services.jsx";
import Contact from "./pages/Contact.jsx";
import Blog from "./pages/Blog.jsx";
import Calculator from "./pages/Calculator.jsx";
import Resources from "./pages/Resources.jsx";
import Booking from "./pages/Booking.jsx";
import InteractiveTools from "./pages/InteractiveTools.jsx";

// Admin pages
import AdminLogin from "./pages/admin/AdminLogin.jsx";
import AdminDashboard from "./pages/admin/AdminDashboard.jsx";
import AdminProjects from "./pages/admin/AdminProjects.jsx";
import AdminSkills from "./pages/admin/AdminSkills.jsx";
import AdminPersonal from "./pages/admin/AdminPersonal.jsx";
import AdminServices from "./pages/admin/AdminServices.jsx";
import AdminTestimonials from "./pages/admin/AdminTestimonials.jsx";
import AdminSettings from "./pages/admin/AdminSettings.jsx";
import AdminTechnologies from "./pages/admin/AdminTechnologies.jsx";
import AdminAnalytics from "./pages/admin/AdminAnalytics.jsx";
import AdminSocialLinks from "./pages/admin/AdminSocialLinks.jsx";
import AdminProcessSteps from "./pages/admin/AdminProcessSteps.jsx";
import AdminResources from "./pages/admin/AdminResources.jsx";
import AdminBlog from "./pages/admin/AdminBlog.jsx";
import AdminContacts from "./pages/admin/AdminContacts.jsx";

function App() {
  return (
    <div className="App">
      <ThemeProvider>
        <LanguageProvider>
          <BrowserRouter>
            <Routes>
              {/* Admin Routes - Also wrapped in ThemeProvider */}
              <Route path="/admin/login" element={<AdminLogin />} />
              <Route path="/admin/dashboard" element={<AdminDashboard />} />
              <Route path="/admin/projects" element={<AdminProjects />} />
              <Route path="/admin/skills" element={<AdminSkills />} />
              <Route path="/admin/personal" element={<AdminPersonal />} />
              <Route path="/admin/services" element={<AdminServices />} />
              <Route path="/admin/testimonials" element={<AdminTestimonials />} />
              <Route path="/admin/technologies" element={<AdminTechnologies />} />
              <Route path="/admin/statistics" element={<AdminAnalytics />} />
              <Route path="/admin/social-links" element={<AdminSocialLinks />} />
              <Route path="/admin/process-steps" element={<AdminProcessSteps />} />
              <Route path="/admin/resources" element={<AdminResources />} />
              <Route path="/admin/blog" element={<AdminBlog />} />
              <Route path="/admin/contacts" element={<AdminContacts />} />
              <Route path="/admin/settings" element={<AdminSettings />} />
              
              {/* Public Routes */}
              <Route path="/*" element={
                <Layout>
                  <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/about" element={<About />} />
                    <Route path="/skills" element={<Skills />} />
                    <Route path="/projects" element={<Projects />} />
                    <Route path="/services" element={<Services />} />
                    <Route path="/contact" element={<Contact />} />
                    <Route path="/blog" element={<Blog />} />
                    <Route path="/calculator" element={<Calculator />} />
                    <Route path="/booking" element={<Booking />} />
                    <Route path="/tools" element={<InteractiveTools />} />
                    <Route path="/resources" element={<Resources />} />
                  </Routes>
                </Layout>
              } />
            </Routes>
          </BrowserRouter>
        </LanguageProvider>
      </ThemeProvider>
    </div>
  );
}

export default App;