import client from "@api/clan/client";
import { DataSchema } from ".";

export type MachineData = {
  // TODO: don't use nested fields, it makes updating data much more complex
  // because we need to deal with deep merging and check if the whole object
  // is missing or not
  deploy?: {
    buildHost?: string;
    targetHost?: string;
  };
  description?: string;
  icon?: string;
  installedAt?: number;
  machineClass: "nixos" | "darwin";
  tags: string[];
};

export type MachineMeta = {
  // TODO: name should be renamed to id
  name: string;
  data: MachineData;
  instanceRefs: string[];
  status: MachineStatus;
  schema: DataSchema;
};

export type MachineStatus =
  | "not_installed"
  | "offline"
  | "out_of_sync"
  | "online";

// TODO: make this one API call only
export async function getMachines(
  clanId: string,
): Promise<Record<string, MachineMeta>> {
  // TODO: make this a GET instead
  const res = await client.post("list_machines", {
    body: {
      flake: {
        identifier: clanId,
      },
    },
  });
  return Object.fromEntries(
    await Promise.all(
      Object.entries(res.data).map(async ([machineName, machine]) => {
        const [stateRes, schemaRes] = await Promise.all([
          client.post("get_machine_state", {
            body: {
              machine: {
                name: machineName,
                flake: {
                  identifier: clanId,
                },
              },
            },
          }),
          client.post("get_machine_fields_schema", {
            body: {
              machine: {
                name: machineName,
                flake: {
                  identifier: clanId,
                },
              },
            },
          }),
        ]);
        return [
          machineName,
          {
            name: machineName,
            data: machine.data,
            instanceRefs: machine.instance_refs,
            status: stateRes.data.status,
            schema: schemaRes.data,
          },
        ];
      }),
    ),
  );
}

// TODO: backend should provide an API that allows partial update
export async function updateMachineData(
  clanId: string,
  machineName: string,
  data: MachineData,
): Promise<void> {
  await client.post("set_machine", {
    body: {
      machine: {
        name: machineName,
        flake: {
          identifier: clanId,
        },
      },
      update: data,
    },
  });
}

export async function updateMachine({
  clan,
  name,
  targetHost,
  port,
  password,
  signal,
}: {
  clan: string;
  name: string;
  targetHost: string;
  port?: number;
  password?: string;
  signal?: AbortSignal;
}): Promise<void> {
  await client.post("run_machine_update", {
    signal,
    body: {
      machine: {
        flake: { identifier: clan },
        name,
      },
      build_host: null,
      target_host: {
        address: targetHost,
        port,
        password,
        ssh_options: {
          StrictHostKeyChecking: "no",
          UserKnownHostsFile: "/dev/null",
        },
      },
    },
  });
}

export async function installMachine({
  clan,
  name,
  targetHost,
  port,
  password,
  signal,
}: {
  clan: string;
  name: string;
  targetHost: string;
  port?: number;
  password?: string;
  signal?: AbortSignal;
}): Promise<void> {
  await client.post("run_machine_install", {
    signal,
    body: {
      opts: {
        machine: {
          name,
          flake: {
            identifier: clan,
          },
        },
      },
      target_host: {
        address: targetHost,
        port,
        password,
        ssh_options: {
          StrictHostKeyChecking: "no",
          UserKnownHostsFile: "/dev/null",
        },
      },
    },
  });
}
