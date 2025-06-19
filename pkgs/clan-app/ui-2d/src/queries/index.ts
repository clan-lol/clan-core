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

export const tagsQuery = (uri: string | undefined) =>
  useQuery<string[]>(() => ({
    queryKey: [uri, "tags"],
    placeholderData: [],
    queryFn: async () => {
      if (!uri) return [];

      const response = await callApi("get_inventory", {
        flake: { identifier: uri },
      }).promise;
      if (response.status === "error") {
        console.error("Failed to fetch data");
      } else {
        const machines = response.data.machines || {};
        const tags = Object.values(machines).flatMap((m) => m.tags || []);
        return tags;
      }
      return [];
    },
  }));

export const machinesQuery = (uri: string | undefined) =>
  useQuery<string[]>(() => ({
    queryKey: [uri, "machines"],
    placeholderData: [],
    queryFn: async () => {
      if (!uri) return [];

      const response = await callApi("get_inventory", {
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
