import { useQuery, UseQueryResult } from "@tanstack/solid-query";
import { callApi, SuccessData } from "../hooks/api";

export type ListMachines = SuccessData<"list_machines">;

export type MachinesQueryResult = UseQueryResult<ListMachines>;

interface MachinesQueryParams {
  clanURI: string | null;
}
export const useMachinesQuery = (props: MachinesQueryParams) =>
  useQuery<ListMachines>(() => ({
    queryKey: ["clans", props.clanURI, "machines"],
    enabled: !!props.clanURI,
    queryFn: async () => {
      if (!props.clanURI) {
        return {};
      }
      const api = callApi("list_machines", {
        flake: {
          identifier: props.clanURI,
        },
      });
      const result = await api.result;
      if (result.status === "error") {
        console.error("Error fetching machines:", result.errors);
        return {};
      }
      return result.data;
    },
  }));
