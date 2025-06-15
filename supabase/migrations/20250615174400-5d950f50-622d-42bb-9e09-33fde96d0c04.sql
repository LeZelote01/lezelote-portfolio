
-- Ajouter la colonne pour le nom anglais de la compétence
ALTER TABLE public.skills ADD COLUMN name_en text;

-- Si tu veux que ce soit obligatoire pour chaque compétence :
-- ALTER TABLE public.skills ALTER COLUMN name_en SET NOT NULL;
