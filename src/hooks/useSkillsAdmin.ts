
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

// CRUD skills (admin only)
export function useSkillsAdmin() {
  const queryClient = useQueryClient();

  // Fetch all skills
  const query = useQuery({
    queryKey: ["admin", "skills"],
    queryFn: async () => {
      const { data, error } = await supabase.from("skills").select("*").order("created_at", { ascending: true });
      if (error) throw new Error(error.message);
      return data ?? [];
    }
  });

  // Create skill
  const create = useMutation({
    mutationFn: async ({ name, level }: { name: string; level: string }) => {
      const { data, error } = await supabase.from("skills").insert([{ name, level }]).select();
      if (error) throw new Error(error.message);
      return data?.[0];
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "skills"] }),
  });

  // Update skill
  const update = useMutation({
    mutationFn: async ({ id, name, level }: { id: string; name: string; level: string }) => {
      const { data, error } = await supabase.from("skills").update({ name, level }).eq("id", id).select();
      if (error) throw new Error(error.message);
      return data?.[0];
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "skills"] }),
  });

  // Delete skill
  const remove = useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase.from("skills").delete().eq("id", id);
      if (error) throw new Error(error.message);
      return id;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "skills"] }),
  });

  return { ...query, create, update, remove };
}
