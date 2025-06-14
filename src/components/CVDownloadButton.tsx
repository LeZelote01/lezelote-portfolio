
const CVDownloadButton = () => (
  <a
    href="/cv.pdf"
    download
    className="bg-secondary text-secondary-foreground rounded px-5 py-2 hover:bg-primary hover:text-primary-foreground transition-all font-semibold shadow-sm border"
    title="Télécharger mon CV"
  >
    Télécharger CV
  </a>
);
export default CVDownloadButton;
