import client from "@api/clan/client";

export interface MachineData {
  name: string;
  deploy: {
    buildHost?: string | null;
    targetHost?: string | null;
  };
  description?: string;
  icon?: string;
  installedAt?: number;
  machineClass: "nixos" | "darwin";
  tags: string[];
}

export interface MachineMeta {
  data: MachineData;
  instanceRefs: string[];
  status: MachineStatus;
}

export type MachineStatus =
  | "not_installed"
  | "offline"
  | "out_of_sync"
  | "online";

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
        const res = await client.post("get_machine_state", {
          body: {
            machine: {
              name: machineName,
              flake: {
                identifier: clanId,
              },
            },
          },
        });
        return [
          machineName,
          {
            data: machine.data,
            instanceRefs: machine.instance_refs,
            status: res.data.status,
          },
        ];
      }),
    ),
  );
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
