import { BlockDevice, FlashInstallerOptions } from "../../sys";
import client from "./client/rpc";

export async function pickFile({
  title,
  initialPath,
}: { title?: string; initialPath?: string } = {}): Promise<string> {
  const res = await client.call("get_system_file", {
    body: {
      file_request: {
        mode: "get_system_file",
        title,
        initial_folder: initialPath,
      },
    },
  });
  return res.data![0];
}

export async function pickDir({
  title,
  initialPath,
}: { title?: string; initialPath?: string } = {}): Promise<string> {
  const res = await client.call("get_system_file", {
    body: {
      file_request: {
        mode: "select_folder",
        title,
        initial_folder: initialPath,
      },
    },
  });
  return res.data![0];
}

export async function pickClanDir(): Promise<string> {
  const res = await client.call("get_clan_folder");
  return res.data.identifier;
}

export async function getFlashableDevices(): Promise<BlockDevice[]> {
  const res = await client.call("list_system_storage_devices");
  return res.data.blockdevices.flatMap((device) => {
    if (device.ro) {
      return [];
    }
    // we only want writeable block devices which are USB or MMC (SD cards)
    const result = /^(?:usb|mmc)-([^-]+)/.exec(device.id_link);
    if (!result) {
      return [];
    }
    const name = result[1];
    return {
      name,
      size: device.size,
      path: device.path,
    };
  });
}

export async function flashInstaller(
  opts: FlashInstallerOptions,
): Promise<void> {
  await client.call("run_machine_flash", {
    body: {
      machine: {
        name: "flash-installer",
        flake: {
          identifier: "https://git.clan.lol/clan/clan-core/archive/main.tar.gz",
        },
      },
      system_config: {
        ssh_keys_path: [opts.sshKeysDir],
      },
      disks: [
        {
          name: "main",
          device: opts.diskPath,
        },
      ],
    },
  });
}
