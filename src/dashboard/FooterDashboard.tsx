
const FooterDashboard = () => (
  <footer className="border-t border-fuchsia-200 mt-10 py-6 bg-gradient-to-r from-fuchsia-100 via-fuchsia-200 to-pink-100 dark:from-fuchsia-950 dark:via-fuchsia-900 dark:to-pink-950 shadow-inner px-6 sm:px-8">
    <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2 text-center sm:text-left">
      <span className="text-xs text-fuchsia-900 dark:text-fuchsia-200 font-medium">© {new Date().getFullYear()} Admin Dashboard. Tous droits réservés.</span>
      <span className="text-xs text-fuchsia-900 dark:text-fuchsia-200">Réalisé avec <span className="text-primary font-bold">Lovable</span> &amp; React</span>
    </div>
  </footer>
);
export default FooterDashboard;
