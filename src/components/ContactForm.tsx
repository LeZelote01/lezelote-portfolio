import { useState } from "react";
import { toast } from "@/hooks/use-toast";
import { useTranslation } from "react-i18next";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Button } from "./ui/button";
import { supabase } from "@/integrations/supabase/client";
import { Linkedin, Twitter, Facebook, Send, Mail } from "lucide-react";

const emailRegex = /^[\w-.]+@([\w-]+\.)+[\w-]{2,}$/i;

const SOCIAL_LINKS = [
  {
    name: "Facebook",
    icon: Facebook,
    url: "https://facebook.com/votreprofil", // Remplace par ton vrai lien Facebook
  },
  {
    name: "Twitter",
    icon: Twitter,
    url: "https://twitter.com/votreprofil", // Remplace par ton vrai lien Twitter
  },
  {
    name: "LinkedIn",
    icon: Linkedin,
    url: "https://linkedin.com/in/votre-profil", // Remplace par ton vrai lien LinkedIn
  },
  {
    name: "Telegram",
    icon: Send,
    url: "https://t.me/votreprofil", // Remplace par ton vrai lien Telegram
  },
  {
    name: "Gmail",
    icon: Mail,
    url: "mailto:ton.email@gmail.com", // Remplace par ton vrai e-mail
  }
];

const ContactForm = () => {
  const [fields, setFields] = useState({ name: "", email: "", message: "" });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{ name?: string; email?: string; message?: string }>({});
  const { t } = useTranslation();

  function validate() {
    const errs: typeof errors = {};
    if (!fields.name || fields.name.length < 2) {
      errs.name = t("contact.invalid_name");
    }
    if (!emailRegex.test(fields.email)) {
      errs.email = t("contact.invalid_email");
    }
    if (!fields.message || fields.message.length < 10) {
      errs.message = t("contact.invalid_message");
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    setFields(f => ({ ...f, [e.target.name]: e.target.value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);

    const { error } = await supabase.from("messages").insert([
      {
        name: fields.name,
        email: fields.email,
        message: fields.message,
      },
    ]);

    setLoading(false);

    if (error) {
      toast({
        title: t("contact.error"),
        description: t("contact.error_detail"),
        variant: "destructive",
      });
      return;
    }

    setFields({ name: "", email: "", message: "" });
    setErrors({});
    toast({ title: t("contact.sent"), description: t("contact.success") });
  }

  return (
    <form className="space-y-6 bg-card rounded-lg shadow p-8 max-w-md mx-auto" onSubmit={handleSubmit} noValidate>
      <h2 className="text-2xl font-bold mb-2 text-primary">{t("contact.title")}</h2>
      <div>
        <label className="block text-sm font-medium mb-1" htmlFor="contact-name">{t("contact.name")}</label>
        <Input
          id="contact-name"
          type="text"
          name="name"
          required
          autoComplete="off"
          value={fields.name}
          onChange={handleChange}
        />
        {errors.name && <div className="text-destructive text-xs mt-1">{errors.name}</div>}
      </div>
      <div>
        <label className="block text-sm font-medium mb-1" htmlFor="contact-email">{t("contact.email")}</label>
        <Input
          id="contact-email"
          type="email"
          name="email"
          required
          autoComplete="off"
          value={fields.email}
          onChange={handleChange}
        />
        {errors.email && <div className="text-destructive text-xs mt-1">{errors.email}</div>}
      </div>
      <div>
        <label className="block text-sm font-medium mb-1" htmlFor="contact-message">{t("contact.message")}</label>
        <Textarea
          id="contact-message"
          name="message"
          required
          rows={4}
          value={fields.message}
          onChange={handleChange}
        />
        {errors.message && <div className="text-destructive text-xs mt-1">{errors.message}</div>}
      </div>
      <Button
        type="submit"
        className="font-semibold w-full"
        disabled={loading}
      >
        {loading ? t("contact.sending") : t("contact.submit")}
      </Button>
      {/* Réseaux sociaux sous le formulaire */}
      <div className="pt-7 border-t border-border mt-6 flex flex-col items-center">
        <span className="text-sm font-medium text-muted-foreground mb-3">
          {t("contact.socials") ?? "Retrouvez-moi sur les réseaux sociaux"}
        </span>
        <div className="flex flex-row gap-5">
          {SOCIAL_LINKS.map(({ name, icon: Icon, url }) => (
            <a
              key={name}
              href={url}
              target="_blank"
              rel={name === "Gmail" ? undefined : "noopener noreferrer"}
              aria-label={name}
              className="rounded-full bg-background border border-border p-2 hover:bg-primary/10 dark:hover:bg-primary/40 transition-transform hover:-translate-y-1"
            >
              <Icon size={28} />
            </a>
          ))}
        </div>
      </div>
    </form>
  );
};

export default ContactForm;
