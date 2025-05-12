import { createQuery } from "@tanstack/solid-query";
import { callApi } from "../api";
import toast from "solid-toast";

export interface ModulesFilter {
  features: string[];
}
export const createModulesQuery = (
  uri: string | null,
  filter?: ModulesFilter,
) =>
  createQuery(() => ({
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
        });
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

export const tagsQuery = (uri: string | null) =>
  createQuery<string[]>(() => ({
    queryKey: [uri, "tags"],
    placeholderData: [],
    queryFn: async () => {
      if (!uri) return [];

      const response = await callApi("get_inventory", {
        flake: { identifier: uri },
      });
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

export const machinesQuery = (uri: string | null) =>
  createQuery<string[]>(() => ({
    queryKey: [uri, "machines"],
    placeholderData: [],
    queryFn: async () => {
      if (!uri) return [];

      const response = await callApi("get_inventory", {
        flake: { identifier: uri },
      });
      if (response.status === "error") {
        console.error("Failed to fetch data");
      } else {
        const machines = response.data.machines || {};
        return Object.keys(machines);
      }
      return [];
    },
  }));
