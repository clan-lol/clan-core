import client from "$clan-api-client";
import {
  InstallMachineOptions,
  InstallMachineProgress,
  MachineDataChange,
  MachineDiskTemplatesOutput,
  MachineHardwareReport,
  MachineOutput,
  machinePositions,
  MachineSSH,
  MachineVarsPromptGroupsOutput,
  MachineVarsPromptsOutput,
  UpdateMachineOptions,
} from "../../machine/machine";
import { mapObjectValues } from "@/util";
import { ClanMessageHandler, onMessage } from "./event";
// TODO: backend should provide an API that allows partial update
export async function updateMachineData(
  machineId: string,
  clanId: string,
  data: MachineDataChange,
): Promise<void> {
  const { position, ...d } = data;
  await client.call("set_machine", {
    body: {
      machine: {
        name: machineId,
        flake: {
          identifier: clanId,
        },
      },
      update: d,
    },
  });
}

export async function deleteMachine(
  machineId: string,
  clanId: string,
): Promise<void> {
  await client.call("delete_machine", {
    body: {
      machine: { flake: { identifier: clanId }, name: machineId },
    },
  });
}

export async function isMachineSSHable(ssh: MachineSSH) {
  try {
    await client.call("check_machine_ssh_login", {
      body: {
        remote: {
          ...ssh,
          ssh_options: {
            StrictHostKeyChecking: "no",
            UserKnownHostsFile: "/dev/null",
          },
        },
      },
    });
  } catch (err) {
    return false;
  }
  return true;
}

export async function getMachineHardwareReport(
  machineId: string,
  clanId: string,
): Promise<MachineHardwareReport | null> {
  const res = await client.call("get_machine_hardware_summary", {
    body: {
      machine: {
        flake: {
          identifier: clanId,
        },
        name: machineId,
      },
    },
  });
  return res.data.hardware_config === "none"
    ? null
    : {
        type: res.data.hardware_config,
      };
}

export async function generateMachineHardwareReport(
  ssh: MachineSSH,
  machineId: string,
  clanId: string,
): Promise<MachineHardwareReport | null> {
  const res = await client.call("run_machine_hardware_info_init", {
    body: {
      target_host: {
        address: ssh.address,
        port: ssh.port,
        password: ssh.password,
        host_key_check: "none",
      },
      opts: {
        machine: {
          flake: {
            identifier: clanId,
          },
          name: machineId,
        },
      },
    },
  });
  return res.data === "none"
    ? null
    : {
        type: res.data,
      };
}

export async function getMachineDiskTemplates(
  machineId: string,
  clanId: string,
): Promise<MachineDiskTemplatesOutput> {
  const res = await client.call("get_machine_disk_schemas", {
    body: {
      machine: {
        flake: {
          identifier: clanId,
        },
        name: machineId,
      },
    },
  });
  return mapObjectValues(res.data, ([, template]) => ({
    name: template.name,
    description: template.frontmatter.description,
    placeholders: mapObjectValues(template.placeholders, ([, placeholder]) => ({
      name: placeholder.label,
      values: placeholder.options!,
      required: placeholder.required,
    })),
  }));
}

export async function getMachineVarsPromptGroups(
  machineId: string,
  clanId: string,
): Promise<MachineVarsPromptGroupsOutput> {
  const res = await client.call("get_generators", {
    body: {
      machines: [
        {
          name: machineId,
          flake: {
            identifier: clanId,
          },
        },
      ],
      // TODO: Make this configurable
      full_closure: false,
    },
  });

  // Collect all prompts that have persist=true
  const persistedPrompts: { generatorName: string; promptName: string }[] = [];
  for (const generator of res.data) {
    for (const prompt of generator.prompts) {
      if (prompt.persist) {
        persistedPrompts.push({
          generatorName: generator.name,
          promptName: prompt.name,
        });
      }
    }
  }

  // Fetch previous values for persisted prompts
  const previousValues =
    persistedPrompts.length > 0
      ? await getPreviousPromptValues(machineId, clanId, persistedPrompts)
      : {};

  const groups: MachineVarsPromptGroupsOutput = {};
  for (const generator of res.data) {
    for (const prompt of generator.prompts) {
      const groupId = prompt.display?.group || "";
      let group: MachineVarsPromptsOutput;
      if (!(groupId in groups)) {
        group = groups[groupId] = {};
      } else {
        group = groups[groupId];
      }
      const key = `${generator.name}/${prompt.name}`;
      group[prompt.name] = {
        generator: generator.name,
        type: prompt.prompt_type,
        description: prompt.description,
        name: prompt.display?.label || prompt.name,
        value: previousValues[key] || "",
        required: prompt.display?.required ?? false,
      };
    }
  }
  return groups;
}

export async function getPreviousPromptValues(
  machineId: string,
  clanId: string,
  promptIds: { generatorName: string; promptName: string }[],
): Promise<Record<string, string>> {
  const res = await client.call("get_generator_prompt_previous_values", {
    body: {
      machine: { name: machineId, flake: { identifier: clanId } },
      prompt_identifiers: promptIds.map((id) => ({
        generator_name: id.generatorName,
        prompt_name: id.promptName,
      })),
    },
  });

  return Object.fromEntries(
    res.data
      .filter(
        (
          r,
        ): r is {
          generator_name: string;
          prompt_name: string;
          value: string;
        } => r.value !== null,
      )
      .map((r) => [`${r.generator_name}/${r.prompt_name}`, r.value]),
  );
}

export async function createMachine(
  machineId: string,
  data: MachineDataChange,
  clanId: string,
): Promise<MachineOutput> {
  const res = await client.call("create_machine", {
    body: {
      opts: {
        clan_dir: {
          identifier: clanId,
        },
        machine: {
          deploy: data.deploy,
          description: data.description,
          machineClass: data.machineClass,
          tags: data.tags,
          name: machineId,
        },
      },
    },
  });
  const clanMachinePositions = machinePositions.getOrSetForClan(clanId);
  // FIXME: handle created instances
  return {
    data: {
      deploy: {
        buildHost: res.data.data.deploy.buildHost || "",
        targetHost: res.data.data.deploy.targetHost || "",
      },
      description: res.data.data.description || "",
      machineClass: res.data.data.machineClass,
      tags: res.data.data.tags,
      position: data.position
        ? clanMachinePositions.setPosition(machineId, data.position)
        : clanMachinePositions.getOrSetPosition(machineId),
    },
    dataSchema: {},
    status: "not_installed",
  };
}

export async function installMachine(
  opts: InstallMachineOptions,
  machineId: string,
  clanId: string,
): Promise<void> {
  await client.call("set_machine_disk_schema", {
    signal: opts.signal,
    body: {
      machine: {
        flake: {
          identifier: clanId,
        },
        name: machineId,
      },
      schema_name: "single-disk",
      placeholders: {
        mainDisk: opts.diskPath,
      },
      force: true,
    },
  });
  opts.onProgress?.("disk");
  await client.call("run_generators", {
    signal: opts.signal,
    body: {
      // Extract generator names from prompt values
      // TODO: This is wrong. We need to extend run_generators to be able to compute
      //       a sane closure over a list of provided generators.
      generators: Object.keys(opts.varsPromptValues),
      prompt_values: opts.varsPromptValues,
      machines: [
        {
          name: machineId,
          flake: {
            identifier: clanId,
          },
        },
      ],
    },
  });
  opts.onProgress?.("varsPrompts");
  const onProgress = opts.onProgress;
  let handler: ClanMessageHandler;
  if (onProgress) {
    handler = (msg) => onProgress(msg.type as InstallMachineProgress);
    onMessage.addListener("run_machine_install", handler);
  }
  try {
    await client.call("run_machine_install", {
      signal: opts.signal,
      body: {
        opts: {
          machine: {
            name: machineId,
            flake: {
              identifier: clanId,
            },
          },
        },
        target_host: {
          address: opts.ssh.address,
          port: opts.ssh.port,
          password: opts.ssh.password,
          host_key_check: "none",
        },
      },
    });
  } finally {
    if (onProgress) {
      onMessage.removeListener("run_machine_install", handler!);
    }
  }
}

export async function updateMachine(
  opts: UpdateMachineOptions,
  machineId: string,
  clanId: string,
): Promise<void> {
  const onProgress = opts.onProgress;
  let handler: ClanMessageHandler;
  if (onProgress) {
    handler = (msg) => onProgress(msg.type as InstallMachineProgress);
    onMessage.addListener("run_machine_update", handler);
  }
  try {
    await client.call("run_machine_update", {
      signal: opts.signal,
      body: {
        machine: {
          flake: { identifier: clanId },
          name: machineId,
        },
        build_host: null,
        target_host: {
          address: opts.ssh.address,
          port: opts.ssh.port,
          password: opts.ssh.password,
          host_key_check: "none",
        },
      },
    });
  } finally {
    if (onProgress) {
      onMessage.removeListener("run_machine_update", handler!);
    }
  }
}
