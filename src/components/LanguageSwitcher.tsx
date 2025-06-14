
import { useTranslation } from "react-i18next";
import { Button } from "./ui/button";

const LANGS: Record<string, string> = {
  fr: "🇫🇷 FR",
  en: "🇬🇧 EN"
};

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();
  const current = i18n.language;

  return (
    <div className="flex gap-1">
      {Object.entries(LANGS).map(([lng, label]) => (
        <Button
          size="sm"
          key={lng}
          variant={lng === current ? "default" : "ghost"}
          onClick={() => i18n.changeLanguage(lng)}
        >
          {label}
        </Button>
      ))}
    </div>
  );
}
