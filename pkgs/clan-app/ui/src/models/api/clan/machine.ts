import client from "./client-call";
import { Machine, MachineData, MachineEntity } from "../../machine/machine";
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

// TODO: make this one API call only
export async function createMachine(machine: Machine): Promise<void> {
  await client.post("create_machine", {
    body: {
      opts: {
        clan_dir: {
          identifier: machine.clan.id,
        },
        machine: {
          ...machine.data,
          name: machine.id,
        },
      },
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
