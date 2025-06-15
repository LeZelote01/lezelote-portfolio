
# Sleek Pro Portfolio Hub

[Projet généré avec Lovable](https://lovable.dev/projects/ccbec7fa-1331-4132-8692-1779c9a7da23)

## 🚀 Aperçu

Portfolio professionnel sous Vite + React + Supabase + shadcn/ui + Tailwind CSS.

---

## ⚡️ Installation Locale

```sh
git clone <URL_DU_DEPOT_GITHUB>
cd <nom_du_dossier>
npm install
npm run dev
```

## 🔐 Variables d'environnement à définir

Ce projet nécessite la configuration des variables d’environnement suivantes, à définir sur Render (ou dans un fichier `.env.local` pour usage local) :

| Variable                    | Exemple                                                                                              | Description                                                        |
|-----------------------------|------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| SUPABASE_URL                | https://vujoahxiytoxxkrqfnzb.supabase.co                                                             | URL de votre projet Supabase                                       |
| SUPABASE_ANON_KEY           | eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdX... (clé complète fournie par Supabase)           | Clé publique d’accès anonyme Supabase (Project Settings > API)     |

*NB : Pour Lovable, ces variables sont déjà intégrées par défaut dans les fichiers sources ; sur Render il faut les ajouter à la main !*

---

## 🛫 Déploiement sur Render

1. **Pousser votre code sur GitHub**
2. **Créer un nouveau Web Service ou Static Site sur [Render](https://render.com/)**
3. **Relier votre repo GitHub**

### Configuration Render :

Pour un web service :

- **Build Command**: `npm install && npm run build`
- **Start Command**: `npm run preview`
- **Root Directory**: _(laissez vide si le projet est à la racine)_

Pour un static site :

- **Build Command**: `npm install && npm run build`
- **Publish Directory**: `dist`
- **Start Command**: _(laisser vide)_

### Variables d'environnement Render

Ajouter dans "Environment" de Render :

- `SUPABASE_URL` = `https://vujoahxiytoxxkrqfnzb.supabase.co`
- `SUPABASE_ANON_KEY` = 
  ```
  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1am9haHhpeXRveHhrcnFmbnpiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk5MTg1NDMsImV4cCI6MjA2NTQ5NDU0M30.74zH1jWzkf5jI5Go6LcGvkhp9lmyee_JoEOAXlhJzlg
  ```

> **Astuce** : changez la clé si vous utilisez votre propre instance Supabase !

---

## 🌍 Lancer l’application

Après déploiement, Render indique l’URL publique de votre site. Tout doit fonctionner immédiatement (CV, authentification admin…).

---

### 📄 Gestion des fichiers CV (Supabase Storage)

- Le bucket **cv** doit exister sur Supabase : [Documentation Storage](https://supabase.com/docs/guides/storage)
- Vérifiez que le "Bucket" est bien public pour permettre les accès et téléchargements.

---

## 📝 Licence

Ce projet est diffusé sous licence MIT. Voir le fichier [`LICENSE`](./LICENSE).

