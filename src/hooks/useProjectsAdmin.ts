
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

// CRUD projets (admin only)
export function useProjectsAdmin() {
  const queryClient = useQueryClient();

  // Fetch all projects
  const query = useQuery({
    queryKey: ["admin", "projects"],
    queryFn: async () => {
      const { data, error } = await supabase.from("projects").select("*").order("created_at", { ascending: false });
      if (error) throw new Error(error.message);
      return data ?? [];
    }
  });

  // Create project
  const create = useMutation({
    mutationFn: async (project: { title: string; description?: string; image_url?: string; link?: string }) => {
      const { data, error } = await supabase.from("projects").insert([project]).select();
      if (error) throw new Error(error.message);
      return data?.[0];
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "projects"] }),
  });

  // Update project
  const update = useMutation({
    mutationFn: async ({ id, ...rest }: { id: string; title?: string; description?: string; image_url?: string; link?: string }) => {
      const { data, error } = await supabase.from("projects").update(rest).eq("id", id).select();
      if (error) throw new Error(error.message);
      return data?.[0];
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "projects"] }),
  });

  // Delete project
  const remove = useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase.from("projects").delete().eq("id", id);
      if (error) throw new Error(error.message);
      return id;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "projects"] }),
  });

  return { ...query, create, update, remove };
}
