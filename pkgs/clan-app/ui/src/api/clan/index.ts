import client from "@api/clan/client";

// TODO: allow users to select a template
export async function createClan({
  name,
  path,
  description,
}: {
  name: string;
  path: string;
  description: string;
}): Promise<void> {
  await client.post("create_clan", {
    body: {
      opts: {
        dest: path,
        template: "minimal",
        initial: {
          name,
          description,
        },
      },
    },
  });

  await client.post("create_service_instance", {
    body: {
      flake: {
        identifier: path,
      },
      module_ref: {
        name: "admin",
        input: "clan-core",
      },
      roles: {
        default: {
          tags: {
            all: {},
          },
        },
      },
    },
  });

  await client.post("create_secrets_user", {
    body: {
      flake_dir: path,
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
