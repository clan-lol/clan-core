import client from "./client-call";
import { MachineData } from "@/src/models";
// TODO: backend should provide an API that allows partial update
export async function updateMachineData(
  machineId: string,
  clanId: string,
  data: Partial<MachineData>,
): Promise<void> {
  await client.post("set_machine", {
    body: {
      machine: {
        name: machineId,
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
