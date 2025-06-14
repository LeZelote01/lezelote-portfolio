
import { useState } from "react";
import { toast } from "@/hooks/use-toast";

const ContactForm = () => {
  const [fields, setFields] = useState({ name: "", email: "", message: "" });
  const [loading, setLoading] = useState(false);

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    setFields(f => ({ ...f, [e.target.name]: e.target.value }));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    // Simule l'envoi (pour vraie gestion, brancher Supabase)
    setTimeout(() => {
      setLoading(false);
      setFields({ name: "", email: "", message: "" });
      toast({ title: "Message envoyé", description: "Merci pour ton message, je reviens vite vers toi !" });
    }, 1200);
  }

  return (
    <form className="space-y-6 bg-card rounded-lg shadow p-8 max-w-md mx-auto" onSubmit={handleSubmit}>
      <h2 className="text-2xl font-bold mb-2 text-primary">Contact</h2>
      <div>
        <label className="block text-sm font-medium mb-1">Nom</label>
        <input
          type="text"
          name="name"
          required
          className="w-full rounded border px-3 py-2 focus:outline-none focus:ring focus:border-primary"
          autoComplete="off"
          value={fields.name}
          onChange={handleChange}
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Email</label>
        <input
          type="email"
          name="email"
          required
          className="w-full rounded border px-3 py-2 focus:outline-none focus:ring focus:border-primary"
          autoComplete="off"
          value={fields.email}
          onChange={handleChange}
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Message</label>
        <textarea
          name="message"
          required
          rows={4}
          className="w-full rounded border px-3 py-2 focus:outline-none focus:ring focus:border-primary"
          value={fields.message}
          onChange={handleChange}
        />
      </div>
      <button
        type="submit"
        className="bg-primary text-primary-foreground font-semibold px-6 py-2 mt-2 rounded hover:bg-primary/90 transition-all"
        disabled={loading}
      >
        {loading ? "Envoi..." : "Envoyer"}
      </button>
    </form>
  );
};

export default ContactForm;
