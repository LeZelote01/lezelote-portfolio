
const AboutCard = () => (
  <section className="max-w-4xl mx-auto py-16 px-4 flex flex-col md:flex-row items-center gap-8">
    <img
      src="/photo-1486312338219-ce68d2c6f44d"
      alt="Portrait"
      className="w-40 h-40 rounded-full object-cover shadow"
    />
    <div>
      <h2 className="text-3xl font-bold mb-2 text-primary">À propos de moi</h2>
      <p className="text-muted-foreground mb-4">
        Passionné par le développement web, la gestion de projets et l'innovation. 
        J'aide les entreprises à concevoir et lancer des solutions robustes, élégantes et évolutives. 
        Toujours curieux et en veille sur les nouvelles technologies.
      </p>
      <div className="flex flex-wrap gap-2">
        <span className="bg-primary/10 text-primary text-xs px-3 py-1 rounded">React</span>
        <span className="bg-primary/10 text-primary text-xs px-3 py-1 rounded">Gestion de projet</span>
        <span className="bg-primary/10 text-primary text-xs px-3 py-1 rounded">UI/UX</span>
      </div>
    </div>
  </section>
);
export default AboutCard;
