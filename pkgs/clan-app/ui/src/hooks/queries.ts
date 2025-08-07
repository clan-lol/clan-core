import { useQueries, useQuery, UseQueryResult } from "@tanstack/solid-query";
import { SuccessData } from "../hooks/api";
import { encodeBase64 } from "@/src/hooks/clan";
import { useApiClient } from "./ApiClient";

export type ClanDetails = SuccessData<"get_clan_details">;
export type ClanDetailsWithURI = ClanDetails & { uri: string };

export type Machine = SuccessData<"get_machine">;
export type ListMachines = SuccessData<"list_machines">;
export type MachineDetails = SuccessData<"get_machine_details">;

export type MachinesQueryResult = UseQueryResult<ListMachines>;
export type ClanListQueryResult = UseQueryResult<ClanDetailsWithURI>[];

export const useMachinesQuery = (clanURI: string) => {
  const client = useApiClient();
  return useQuery<ListMachines>(() => ({
    queryKey: ["clans", encodeBase64(clanURI), "machines"],
    queryFn: async () => {
      const api = client.fetch("list_machines", {
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
};

export const useMachineQuery = (clanURI: string, machineName: string) => {
  const client = useApiClient();
  return useQuery<Machine>(() => ({
    queryKey: ["clans", encodeBase64(clanURI), "machine", machineName],
    queryFn: async () => {
      const call = client.fetch("get_machine", {
        name: machineName,
        flake: {
          identifier: clanURI,
        },
      });

      const result = await call.result;
      if (result.status === "error") {
        throw new Error("Error fetching machine: " + result.errors[0].message);
      }

      return result.data;
    },
  }));
};

export const useMachineDetailsQuery = (
  clanURI: string,
  machineName: string,
) => {
  const client = useApiClient();
  return useQuery<MachineDetails>(() => ({
    queryKey: ["clans", encodeBase64(clanURI), "machine_detail", machineName],
    queryFn: async () => {
      const call = client.fetch("get_machine_details", {
        machine: {
          name: machineName,
          flake: {
            identifier: clanURI,
          },
        },
      });

      const result = await call.result;
      if (result.status === "error") {
        throw new Error(
          "Error fetching machine details: " + result.errors[0].message,
        );
      }

      return result.data;
    },
  }));
};

export const useClanDetailsQuery = (clanURI: string) => {
  const client = useApiClient();
  return useQuery<ClanDetails>(() => ({
    queryKey: ["clans", encodeBase64(clanURI), "details"],
    queryFn: async () => {
      const call = client.fetch("get_clan_details", {
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
};

export const useClanListQuery = (clanURIs: string[]): ClanListQueryResult => {
  const client = useApiClient();
  return useQueries(() => ({
    queries: clanURIs.map((clanURI) => ({
      queryKey: ["clans", encodeBase64(clanURI), "details"],
      enabled: !!clanURI,
      queryFn: async () => {
        const call = client.fetch("get_clan_details", {
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
};

