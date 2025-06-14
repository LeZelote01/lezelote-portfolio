
-- === SKILLS ===
ALTER TABLE public.skills ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Public can read skills" ON public.skills;
CREATE POLICY "Public can read skills"
  ON public.skills
  FOR SELECT
  USING (true);

DROP POLICY IF EXISTS "Admins can insert skills" ON public.skills;
CREATE POLICY "Admins can insert skills"
  ON public.skills
  FOR INSERT
  TO authenticated
  WITH CHECK (public.has_role(auth.uid(), 'admin'));

DROP POLICY IF EXISTS "Admins can update skills" ON public.skills;
CREATE POLICY "Admins can update skills"
  ON public.skills
  FOR UPDATE
  TO authenticated
  USING (public.has_role(auth.uid(), 'admin'));

DROP POLICY IF EXISTS "Admins can delete skills" ON public.skills;
CREATE POLICY "Admins can delete skills"
  ON public.skills
  FOR DELETE
  TO authenticated
  USING (public.has_role(auth.uid(), 'admin'));


-- === PROJECTS ===
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Public can read projects" ON public.projects;
CREATE POLICY "Public can read projects"
  ON public.projects
  FOR SELECT
  USING (true);

DROP POLICY IF EXISTS "Admins can insert projects" ON public.projects;
CREATE POLICY "Admins can insert projects"
  ON public.projects
  FOR INSERT
  TO authenticated
  WITH CHECK (public.has_role(auth.uid(), 'admin'));

DROP POLICY IF EXISTS "Admins can update projects" ON public.projects;
CREATE POLICY "Admins can update projects"
  ON public.projects
  FOR UPDATE
  TO authenticated
  USING (public.has_role(auth.uid(), 'admin'));

DROP POLICY IF EXISTS "Admins can delete projects" ON public.projects;
CREATE POLICY "Admins can delete projects"
  ON public.projects
  FOR DELETE
  TO authenticated
  USING (public.has_role(auth.uid(), 'admin'));


-- === USER_ROLES ===
ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "User can see his roles" ON public.user_roles;
CREATE POLICY "User can see his roles"
  ON public.user_roles
  FOR SELECT
  USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Admins can insert roles" ON public.user_roles;
CREATE POLICY "Admins can insert roles"
  ON public.user_roles
  FOR INSERT
  TO authenticated
  WITH CHECK (public.has_role(auth.uid(), 'admin'));

DROP POLICY IF EXISTS "Admins can update roles" ON public.user_roles;
CREATE POLICY "Admins can update roles"
  ON public.user_roles
  FOR UPDATE
  TO authenticated
  USING (public.has_role(auth.uid(), 'admin'));

DROP POLICY IF EXISTS "Admins can delete roles" ON public.user_roles;
CREATE POLICY "Admins can delete roles"
  ON public.user_roles
  FOR DELETE
  TO authenticated
  USING (public.has_role(auth.uid(), 'admin'));
