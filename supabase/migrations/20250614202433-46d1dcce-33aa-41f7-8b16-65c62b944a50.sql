
-- Étape 1 : créer une enum pour les rôles
CREATE TYPE public.app_role AS ENUM ('admin', 'user');

-- Étape 2 : table des rôles par utilisateur
CREATE TABLE public.user_roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  role app_role NOT NULL,
  UNIQUE (user_id, role)
);

-- Étape 3 : RLS (chaque utilisateur ne peut voir que ses rôles)
ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "User can see his roles"
  ON public.user_roles 
  FOR SELECT
  USING (auth.uid() = user_id);

-- RLS SuperAdmin : on gèrera l’édition directement par la DB (il n’y a qu’un admin attribué à la main)

-- Étape 4 : fonction pour vérifier si un user est admin
CREATE OR REPLACE FUNCTION public.has_role(_user_id uuid, _role app_role)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.user_roles WHERE user_id = _user_id AND role = _role
  )
$$;
