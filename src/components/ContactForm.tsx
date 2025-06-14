
import { useState } from "react";
import { toast } from "@/hooks/use-toast";
import { useTranslation } from "react-i18next";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Button } from "./ui/button";

const emailRegex = /^[\w-.]+@([\w-]+\.)+[\w-]{2,}$/i;

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

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setFields({ name: "", email: "", message: "" });
      setErrors({});
      toast({ title: t("contact.sent"), description: t("contact.success") });
    }, 1200);
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
    </form>
  );
};

export default ContactForm;
