import { createStore, SetStoreFunction } from "solid-js/store";
import api from "../api";

export * from "./Context";

export type Sys = object;
export function createSysStore(): readonly [Sys, SysMethods] {
  const [sys, setSys] = createStore<Sys>({});
  return [sys, createSysMethods(sys, setSys)];
}

export type SysMethods = {
  pickFile(opts?: { title?: string; initialPath?: string }): Promise<string>;
  pickDir(opts?: { title?: string; initialPath?: string }): Promise<string>;
  pickClanDir(): Promise<string>;
  getFlashableDevices(): Promise<BlockDevice[]>;
  flashInstaller(opts: FlashInstallerOptions): Promise<void>;
};

export type FlashInstallerOptions = {
  signal?: AbortSignal;
  sshKeysDir: string;
  diskPath: string;
};

export type BlockDeviceEntity = {
  name: string;
  size: string;
  path: string;
};
export type BlockDevice = BlockDeviceEntity;

function createSysMethods(
  _sys: Sys,
  _setSys: SetStoreFunction<Sys>,
): SysMethods {
  const self: SysMethods = {
    async pickFile(opts) {
      return await api.clan.pickFile(opts);
    },
    async pickDir(opts) {
      return await api.clan.pickDir(opts);
    },
    async pickClanDir() {
      return await api.clan.pickClanDir();
    },
    async getFlashableDevices() {
      return await api.clan.getFlashableDevices();
    },
    async flashInstaller(opts) {
      await api.clan.flashInstaller(opts);
    },
  };
  return self;
}
