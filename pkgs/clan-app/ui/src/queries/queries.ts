import { useQueries, useQuery, UseQueryResult } from "@tanstack/solid-query";
import { callApi, SuccessData } from "../hooks/api";
import { encodeBase64 } from "@/src/hooks/clan";

export type ClanDetails = SuccessData<"get_clan_details">;
export type ClanDetailsWithURI = ClanDetails & { uri: string };

export type ListMachines = SuccessData<"list_machines">;
export type MachineDetails = SuccessData<"get_machine_details">;

export type MachinesQueryResult = UseQueryResult<ListMachines>;
export type ClanListQueryResult = UseQueryResult<ClanDetailsWithURI>[];

export const useMachinesQuery = (clanURI: string) =>
  useQuery<ListMachines>(() => ({
    queryKey: ["clans", encodeBase64(clanURI), "machines"],
    queryFn: async () => {
      const api = callApi("list_machines", {
        flake: {
          identifier: clanURI,
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

export const useClanDetailsQuery = (clanURI: string) =>
  useQuery<ClanDetails>(() => ({
    queryKey: ["clans", encodeBase64(clanURI), "details"],
    queryFn: async () => {
      const call = callApi("get_clan_details", {
        flake: {
          identifier: clanURI,
        },
      });
      const result = await call.result;

      if (result.status === "error") {
        // todo should we create some specific error types?
        console.error("Error fetching clan details:", result.errors);
        throw new Error(result.errors[0].message);
      }

      return {
        uri: clanURI,
        ...result.data,
      };
    },
  }));

export const useClanListQuery = (clanURIs: string[]): ClanListQueryResult =>
  useQueries(() => ({
    queries: clanURIs.map((clanURI) => ({
      queryKey: ["clans", encodeBase64(clanURI), "details"],
      enabled: !!clanURI,
      queryFn: async () => {
        const call = callApi("get_clan_details", {
          flake: {
            identifier: clanURI,
          },
        });
        const result = await call.result;

        if (result.status === "error") {
          // todo should we create some specific error types?
          console.error("Error fetching clan details:", result.errors);
          throw new Error(result.errors[0].message);
        }

        return {
          uri: clanURI,
          ...result.data,
        };
      },
    })),
  }));
