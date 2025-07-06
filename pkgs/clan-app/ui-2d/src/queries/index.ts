import { useQuery } from "@tanstack/solid-query";
import { callApi } from "../api";

interface ModulesFilter {
  features: string[];
}
export const createModulesQuery = (
  uri: string | undefined,
  filter?: ModulesFilter,
) =>
  useQuery(() => ({
    queryKey: [uri, "list_modules"],
    placeholderData: {
      localModules: {},
      modulesPerSource: {},
    },
    enabled: !!uri,
    queryFn: async () => {
      if (uri) {
        const response = await callApi("list_modules", {
          base_path: uri,
        }).promise;
        if (response.status === "error") {
          console.error("Failed to fetch data");
        } else {
          return response.data;
        }
      }
      return {
        localModules: {},
        modulesPerSource: {},
      };
    },
  }));

export const machinesQuery = (uri: string | undefined) =>
  useQuery<string[]>(() => ({
    queryKey: [uri, "machines"],
    placeholderData: [],
    queryFn: async () => {
      if (!uri) return [];

      const response = await callApi("list_machines", {
        flake: { identifier: uri },
      }).promise;
      if (response.status === "error") {
        console.error("Failed to fetch data");
      } else {
        const machines = response.data.machines || {};
        return Object.keys(machines);
      }
      return [];
    },
  }));
