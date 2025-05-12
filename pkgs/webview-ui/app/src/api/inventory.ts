import { QueryClient } from "@tanstack/solid-query";
import { ApiEnvelope, callApi } from ".";
import { Schema as Inventory } from "@/api/Inventory";

export async function get_inventory(client: QueryClient, base_path: string) {
  const data = await client.ensureQueryData({
    queryKey: [base_path, "inventory"],
    queryFn: () => {
      console.log("Refreshing inventory");
      return callApi("get_inventory", {
        flake: { identifier: base_path },
      }) as Promise<ApiEnvelope<Inventory>>;
    },
    revalidateIfStale: true,
    staleTime: 60 * 1000,
  });

  return data;
}
