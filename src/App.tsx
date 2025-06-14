import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Skills from "./pages/Skills";
import Projects from "./pages/Projects";
import About from "./pages/About";
import Contact from "./pages/Contact";
import NotFound from "./pages/NotFound";
import DashboardHome from "./dashboard/DashboardHome";
import ProjectsAdmin from "./dashboard/ProjectsAdmin";
import SkillsAdmin from "./dashboard/SkillsAdmin";
import CVAdmin from "./dashboard/CVAdmin";
import AdminLogin from "./pages/AdminLogin";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/skills" element={<Skills />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/about" element={<About />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/dashboard" element={<DashboardHome />} />
          <Route path="/dashboard/projects" element={<ProjectsAdmin />} />
          <Route path="/dashboard/skills" element={<SkillsAdmin />} />
          <Route path="/dashboard/cv" element={<CVAdmin />} />
          {/* Changement ici : login admin */}
          <Route path="/admin" element={<AdminLogin />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
