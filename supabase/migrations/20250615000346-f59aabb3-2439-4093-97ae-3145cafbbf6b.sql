
-- Créer le bucket "cv" en public (aucun changement ici)
insert into storage.buckets 
  (id, name, public) 
values 
  ('cv', 'cv', true)
on conflict (id) do nothing;

-- Policy: lecture publique (aucun changement)
create policy "Public can select CV" on storage.objects
  for select
  using (
    bucket_id = 'cv'
  );

-- Policy: upload réservé aux admins (corrigée)
create policy "Admins can insert CV" on storage.objects
  for insert 
  to authenticated
  with check (
    bucket_id = 'cv' AND 
    exists (
      select 1 from public.user_roles 
      where user_id = auth.uid() and role = 'admin'
    )
  );

-- Policy: modification (update) réservée aux admins
create policy "Admins can update CV" on storage.objects
  for update 
  to authenticated
  using (
    bucket_id = 'cv' AND 
    exists (
      select 1 from public.user_roles 
      where user_id = auth.uid() and role = 'admin'
    )
  );

-- Policy: suppression réservée aux admins
create policy "Admins can delete CV" on storage.objects
  for delete 
  to authenticated
  using (
    bucket_id = 'cv' AND 
    exists (
      select 1 from public.user_roles 
      where user_id = auth.uid() and role = 'admin'
    )
  );
