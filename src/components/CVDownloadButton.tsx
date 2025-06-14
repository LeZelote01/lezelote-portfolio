
const CVDownloadButton = () => (
  <a
    href="/cv.pdf"
    download
    className="bg-gradient-to-r from-fuchsia-600 via-indigo-500 to-purple-400 text-white rounded px-5 py-2 hover:brightness-110 hover:from-purple-700 transition-all font-semibold shadow-md border-0"
    title="Télécharger mon CV"
  >
    Télécharger CV
  </a>
);
export default CVDownloadButton;
