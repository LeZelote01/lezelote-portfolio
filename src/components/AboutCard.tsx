
import { useTranslation } from "react-i18next";

const AboutCard = () => {
  const { t } = useTranslation();

  return (
    <section className="max-w-4xl mx-auto py-16 px-4 flex flex-col md:flex-row items-center gap-8">
      <img
        src="/photo-1486312338219-ce68d2c6f44d"
        alt="Portrait"
        className="w-40 h-40 rounded-full object-cover shadow"
      />
      <div>
        <h2 className="text-3xl font-bold mb-2 text-primary">{t("about.title")}</h2>
        <p className="text-muted-foreground mb-2">{t("about.intro")}</p>
        <p className="text-muted-foreground mb-4">{t("about.main")}</p>
        <div className="mb-2 font-semibold text-fuchsia-800 dark:text-fuchsia-300">{t("about.listTitle")}</div>
        <ul className="flex flex-col gap-1 text-sm text-muted-foreground mb-3">
          <li>{t("about.item1")}</li>
          <li>{t("about.item2")}</li>
          <li>{t("about.item3")}</li>
          <li>{t("about.item4")}</li>
          <li>{t("about.item5")}</li>
        </ul>
        <div className="italic text-xs md:text-sm text-muted-foreground">{t("about.conclusion")}</div>
      </div>
    </section>
  );
};
export default AboutCard;
