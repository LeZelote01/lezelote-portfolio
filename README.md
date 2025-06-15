
# lezelote-portfolio

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

## 🔐 Configuration des variables d'environnement

Avant de lancer le projet (en local ou sur Render), il faut définir quelques variables d'environnement.

### Exemple pour un fichier `.env.local` (recommandé pour le local) :

Crée un fichier `.env.local` à la racine du projet avec ce contenu :
```
SUPABASE_URL=ton_url_supabase
SUPABASE_ANON_KEY=ta_cle_anon_supabase
```
> **Attention** : Ne partage JAMAIS tes vraies clés ou URLs publiques. Ce fichier ne doit pas être versionné.

---

## 🛫 Déploiement sur Render

1. **Pousser ton code sur GitHub**
2. **Créer un nouveau Web Service ou Static Site sur [Render](https://render.com/)**
3. **Relier ton repo GitHub**

### Configuration Render :

Pour un web service :

- **Build Command**: `npm install && npm run build`
- **Start Command**: `npm run preview`
- **Root Directory**: _(laisse vide si le projet est à la racine)_

Pour un static site :

- **Build Command**: `npm install && npm run build`
- **Publish Directory**: `dist`
- **Start Command**: _(laisser vide)_

### Variables d'environnement Render

Ajoute dans l'onglet "Environment" de Render :
- `SUPABASE_URL` = `Insère ici l'URL de ton projet Supabase`
- `SUPABASE_ANON_KEY` = `Insère ici ta clé anonyme Supabase`

> **Astuce** : Ne remplis jamais ces champs avec les exemples du README ! Utilise toujours tes vraies informations Supabase, récupérables dans Supabase > Project Settings > API.

---

## 🌍 Lancer l’application

Après déploiement, Render indique l’URL publique de ton site.

---

### 📄 Gestion des fichiers CV (Supabase Storage)

- Le bucket **cv** doit exister sur Supabase : [Documentation Storage](https://supabase.com/docs/guides/storage)
- Vérifie que le bucket est bien public.

---

## 📝 Licence

Ce projet est diffusé sous licence MIT. Voir le fichier [`LICENSE`](./LICENSE).

