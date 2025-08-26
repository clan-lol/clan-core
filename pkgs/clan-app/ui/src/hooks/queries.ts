import {
  QueryClient,
  useQueries,
  useQuery,
  UseQueryResult,
} from "@tanstack/solid-query";
import { SuccessData } from "../hooks/api";
import { encodeBase64 } from "@/src/hooks/clan";
import { useApiClient } from "./ApiClient";
import { experimental_createQueryPersister } from "@tanstack/solid-query-persist-client";
import { ClanDetailsStore } from "@/src/stores/clanDetails";

export interface ClanDetails {
  uri: string;
  details: SuccessData<"get_clan_details">;
  fieldsSchema: SuccessData<"get_clan_details_schema">;
}

export type Tags = SuccessData<"list_tags">;
export type Machine = SuccessData<"get_machine">;

export type MachineState = SuccessData<"get_machine_state">;
export type MachineStatus = MachineState["status"];

export type ListMachines = SuccessData<"list_machines">;
export type MachineDetails = SuccessData<"get_machine_details">;

export interface MachineDetail {
  tags: Tags;
  machine: Machine;
  fieldsSchema: SuccessData<"get_machine_fields_schema">;
}

export type MachinesQueryResult = UseQueryResult<ListMachines>;
export type ClanListQueryResult = UseQueryResult<ClanDetails>[];

export const DefaultQueryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

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
  return useQuery<MachineDetail>(() => ({
    queryKey: ["clans", encodeBase64(clanURI), "machine", machineName],
    queryFn: async () => {
      const [tagsCall, machineCall, schemaCall] = [
        client.fetch("list_tags", {
          flake: {
            identifier: clanURI,
          },
        }),
        client.fetch("get_machine", {
          name: machineName,
          flake: {
            identifier: clanURI,
          },
        }),
        client.fetch("get_machine_fields_schema", {
          machine: {
            name: machineName,
            flake: {
              identifier: clanURI,
            },
          },
        }),
      ];

      const tags = await tagsCall.result;
      if (tags.status === "error") {
        throw new Error("Error fetching tags: " + tags.errors[0].message);
      }

      const machine = await machineCall.result;
      if (machine.status === "error") {
        throw new Error("Error fetching machine: " + machine.errors[0].message);
      }

      const writeSchema = await schemaCall.result;
      if (writeSchema.status === "error") {
        throw new Error(
          "Error fetching machine fields schema: " +
            writeSchema.errors[0].message,
        );
      }

      return {
        tags: tags.data,
        machine: machine.data,
        fieldsSchema: writeSchema.data,
      };
    },
  }));
};

export const useMachineStateQuery = (clanURI: string, machineName: string) => {
  const client = useApiClient();
  return useQuery<MachineState>(() => ({
    queryKey: ["clans", encodeBase64(clanURI), "machine", machineName, "state"],
    queryFn: async () => {
      const apiCall = client.fetch("get_machine_state", {
        machine: {
          name: machineName,
          flake: {
            identifier: clanURI,
          },
        },
      });

      const result = await apiCall.result;
      if (result.status === "error") {
        throw new Error(
          "Error fetching machine status: " + result.errors[0].message,
        );
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

export const ClanDetailsPersister = experimental_createQueryPersister({
  storage: ClanDetailsStore,
});

export const useClanDetailsQuery = (clanURI: string) => {
  const client = useApiClient();
  return useQuery<ClanDetails>(() => ({
    queryKey: ["clans", encodeBase64(clanURI), "details"],
    persister: ClanDetailsPersister.persisterFn,
    queryFn: async () => {
      const args = {
        flake: {
          identifier: clanURI,
        },
      };

      const [detailsCall, schemaCall] = [
        client.fetch("get_clan_details", args),
        client.fetch("get_clan_details_schema", {
          flake: {
            identifier: clanURI,
          },
        }),
      ];

      const details = await detailsCall.result;

      if (details.status === "error") {
        throw new Error(
          "Error fetching clan details: " + details.errors[0].message,
        );
      }

      const schema = await schemaCall.result;

      if (schema.status === "error") {
        throw new Error(
          "Error fetching clan details schema: " + schema.errors[0].message,
        );
      }

      return {
        uri: clanURI,
        details: details.data!,
        fieldsSchema: schema.data,
      };
    },
  }));
};

export const useClanListQuery = (
  clanURIs: string[],
  activeClanURI?: string,
): ClanListQueryResult => {
  const client = useApiClient();

  return useQueries(() => ({
    queries: clanURIs.map((clanURI) => {
      const queryKey = ["clans", encodeBase64(clanURI), "details"];

      return {
        // eslint-disable-next-line @tanstack/query/exhaustive-deps
        queryKey,
        persister: ClanDetailsPersister.persisterFn,
        queryFn: async () => {
          // we only perform a request for the active clan
          // for all others we load the cached query state
          // this is due to how expensive it currently is to evaluate a flake for clan details
          // it also helps when a clan folder has been moved/renamed
          if (clanURI != activeClanURI) {
            const cached = DefaultQueryClient.getQueryCache().find({
              queryKey,
            });

            if (cached?.state?.data) {
              return cached.state.data;
            }
          }

          const args = {
            flake: {
              identifier: clanURI,
            },
          };

          const [detailsCall, schemaCall] = [
            client.fetch("get_clan_details", args),
            client.fetch("get_clan_details_schema", {
              flake: {
                identifier: clanURI,
              },
            }),
          ];

          const details = await detailsCall.result;

          if (details.status === "error") {
            throw new Error(
              "Error fetching clan details: " + details.errors[0].message,
            );
          }

          const schema = await schemaCall.result;

          if (schema.status === "error") {
            throw new Error(
              "Error fetching clan details schema: " + schema.errors[0].message,
            );
          }

          return {
            uri: clanURI,
            details: details.data,
            fieldsSchema: schema.data,
          };
        },
      };
    }),
  }));
};

export type MachineFlashOptions = SuccessData<"get_machine_flash_options">;
export type MachineFlashOptionsQuery = UseQueryResult<MachineFlashOptions>;

export const useMachineFlashOptions = (): MachineFlashOptionsQuery => {
  const client = useApiClient();
  return useQuery<MachineFlashOptions>(() => ({
    queryKey: ["clans", "machine_flash_options"],
    queryFn: async () => {
      const call = client.fetch("get_machine_flash_options", {});
      const result = await call.result;

      if (result.status === "error") {
        // todo should we create some specific error types?
        console.error("Error fetching clan details:", result.errors);
        throw new Error(result.errors[0].message);
      }

      return result.data;
    },
  }));
};

export type SystemStorageOptions = SuccessData<"list_system_storage_devices">;
export type SystemStorageOptionsQuery = UseQueryResult<SystemStorageOptions>;

export const useSystemStorageOptions = (): SystemStorageOptionsQuery => {
  const client = useApiClient();
  return useQuery<SystemStorageOptions>(() => ({
    queryKey: ["system", "storage_devices"],
    queryFn: async () => {
      const call = client.fetch("list_system_storage_devices", {});
      const result = await call.result;

      if (result.status === "error") {
        // todo should we create some specific error types?
        console.error("Error fetching clan details:", result.errors);
        throw new Error(result.errors[0].message);
      }

      return result.data;
    },
  }));
};

export type MachineHardwareSummary =
  SuccessData<"get_machine_hardware_summary">;
export type MachineHardwareSummaryQuery =
  UseQueryResult<MachineHardwareSummary>;

export const useMachineHardwareSummary = (
  clanUri: string,
  machineName: string,
): MachineHardwareSummaryQuery => {
  const client = useApiClient();
  return useQuery<MachineHardwareSummary>(() => ({
    queryKey: [
      "clans",
      encodeBase64(clanUri),
      "machines",
      machineName,
      "hardware_summary",
    ],
    queryFn: async () => {
      const call = client.fetch("get_machine_hardware_summary", {
        machine: {
          flake: {
            identifier: clanUri,
          },
          name: machineName,
        },
      });
      const result = await call.result;

      if (result.status === "error") {
        // todo should we create some specific error types?
        console.error("Error fetching clan details:", result.errors);
        throw new Error(result.errors[0].message);
      }

      return result.data;
    },
  }));
};

export type MachineDiskSchema = SuccessData<"get_machine_disk_schemas">;
export type MachineDiskSchemaQuery = UseQueryResult<MachineDiskSchema>;

export const useMachineDiskSchemas = (
  clanUri: string,
  machineName: string,
): MachineDiskSchemaQuery => {
  const client = useApiClient();
  return useQuery<MachineDiskSchema>(() => ({
    queryKey: [
      "clans",
      encodeBase64(clanUri),
      "machines",
      machineName,
      "disk_schemas",
    ],
    queryFn: async () => {
      const call = client.fetch("get_machine_disk_schemas", {
        machine: {
          flake: {
            identifier: clanUri,
          },
          name: machineName,
        },
      });
      const result = await call.result;

      if (result.status === "error") {
        // todo should we create some specific error types?
        console.error("Error fetching clan details:", result.errors);
        throw new Error(result.errors[0].message);
      }

      return result.data;
    },
  }));
};

export type MachineGenerators = SuccessData<"get_generators">;
export type MachineGeneratorsQuery = UseQueryResult<MachineGenerators>;

export const useMachineGenerators = (
  clanUri: string,
  machineName: string,
): MachineGeneratorsQuery => {
  const client = useApiClient();
  return useQuery<MachineGenerators>(() => ({
    queryKey: [
      "clans",
      encodeBase64(clanUri),
      "machines",
      machineName,
      "generators",
    ],
    queryFn: async () => {
      const call = client.fetch("get_generators", {
        machines: [
          {
            name: machineName,
            flake: {
              identifier: clanUri,
            },
          },
        ],
        full_closure: true, // TODO: Make this configurable
        // TODO: Make this configurable
        include_previous_values: true,
      });
      const result = await call.result;

      if (result.status === "error") {
        // todo should we create some specific error types?
        console.error("Error fetching clan details:", result.errors);
        throw new Error(result.errors[0].message);
      }

      return result.data;
    },
  }));
};
