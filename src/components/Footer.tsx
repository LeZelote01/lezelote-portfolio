
const Footer = () => (
  <footer className="border-t border-border mt-16 py-6 bg-background">
    <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between px-8 gap-2">
      <span className="text-xs text-muted-foreground">© {new Date().getFullYear()} Mon Portfolio. Tous droits réservés.</span>
      <span className="text-xs text-muted-foreground">Réalisé avec <span className="text-primary font-bold">Lovable</span> &amp; React</span>
    </div>
  </footer>
);
export default Footer;
