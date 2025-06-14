
const Footer = () => (
  <footer className="border-t border-border mt-16 py-6 bg-gradient-to-r from-indigo-100 via-fuchsia-200 to-pink-100 dark:from-gray-900 dark:via-fuchsia-950 dark:to-indigo-950 transition-colors duration-500 shadow-inner">
    <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between px-8 gap-2">
      <span className="text-xs text-fuchsia-900 dark:text-fuchsia-200">© {new Date().getFullYear()} Mon Portfolio. Tous droits réservés.</span>
      <span className="text-xs text-fuchsia-900 dark:text-fuchsia-200">Réalisé avec <span className="text-primary font-bold">Lovable</span> &amp; React</span>
    </div>
  </footer>
);
export default Footer;
