import { Accessor } from "solid-js";
import { SetStoreFunction } from "solid-js/store";
import api from "../api";
import {
  Clan,
  ClanMethods,
  Clans,
  ClansMethods,
  DataSchema,
  Machines,
  MachinesMethods,
  ServiceInstance,
} from "..";
import { DeepImmutable, DeepRequired, mapObjectValues } from "@/util";

export type MachineOutput = {
  readonly data: MachineDataOutput;
  readonly dataSchema: DataSchema;
  readonly status: MachineStatus;
};
export type MachinePosition = readonly [number, number];

export type Machine = Omit<MachineOutput, "data"> & {
  readonly clan: Clan;
  readonly id: string;
  data: MachineData;
  readonly isActive: boolean;
  readonly isHighlighted: boolean;
  readonly serviceInstances: ServiceInstance[];
};
export type MachineDataChange = {
  deploy?: {
    buildHost?: string;
    targetHost?: string;
  };
  description?: string;
  machineClass?: "nixos" | "darwin";
  tags?: string[];
  position?: MachinePosition;
};
export type MachineData = DeepRequired<MachineDataChange>;
export type MachineDataOutput = DeepImmutable<MachineData>;

export type MachineStatus =
  | "not_installed"
  | "offline"
  | "out_of_sync"
  | "online";

export type MachineSSH = {
  address: string;
  port?: number;
  password?: string;
};

export type MachineHardwareReport = {
  readonly type: "nixos-facter" | "nixos-generate-config";
};

export type MachineDiskTemplatesOutput = Record<
  string,
  MachineDiskTemplateOutput
>;
export type MachineDiskTemplateOutput = {
  readonly name: string;
  readonly description: string;
  readonly placeholders: Record<string, MachineDiskTemplatePlaceHolderOutput>;
};
export type MachineDiskTemplatePlaceHolderOutput = {
  readonly name: string;
  readonly values: string[];
  readonly required: boolean;
};

export type MachineDiskTemplates = {
  all: Record<string, MachineDiskTemplate>;
  sorted: MachineDiskTemplate[];
};
export type MachineDiskTemplate = Omit<
  MachineDiskTemplateOutput,
  "placeholders"
> & {
  readonly id: string;
  readonly placeholders: Record<string, MachineDiskTemplatePlaceHolder>;
};
export type MachineDiskTemplatePlaceHolder =
  MachineDiskTemplatePlaceHolderOutput & {
    readonly id: string;
  };

export type MachineVarsPromptGroupsOutput = Record<
  string,
  MachineVarsPromptsOutput
>;
export type MachineVarsPromptsOutput = Record<string, MachineVarsPromptOutput>;
export type MachineVarsPromptOutput = {
  readonly generator: string;
  readonly description: string;
  readonly name: string;
  readonly value: string;
  readonly type: "hidden" | "line" | "multiline" | "multiline-hidden";
  readonly required: boolean;
};

export type MachineVarsPromptGroups = {
  readonly all: Record<string, MachineVarsPromptGroup>;
  readonly sorted: MachineVarsPromptGroup[];
};
export type MachineVarsPromptGroup = {
  readonly id: string;
  readonly prompts: MachineVarsPrompts;
};
export type MachineVarsPrompts = {
  readonly all: Record<string, MachineVarsPrompt>;
  readonly sorted: MachineVarsPrompt[];
};
export type MachineVarsPrompt = MachineVarsPromptOutput & {
  readonly id: string;
};

const CUBE_SPACING = 1;
export class ClanMachinePositions {
  #positions: Record<string, MachinePosition>;
  #positionSet: Set<string>;
  constructor(all: Record<string, MachinePosition>) {
    this.#positions = all;
    this.#positionSet = new Set(Object.values(all).map(posStr));
  }
  getOrSetPosition(machineId: string): MachinePosition {
    if (this.#positions[machineId]) {
      return this.#positions[machineId];
    }
    const pos = this.#nextAvailable();
    this.#positions[machineId] = pos;
    this.#positionSet.add(posStr(pos));
    return pos;
  }
  setPosition(machineId: string, pos: MachinePosition): MachinePosition {
    const oldPos = this.#positions[machineId];
    if (oldPos) {
      this.#positionSet.delete(posStr(oldPos));
    }
    this.#positions[machineId] = pos;
    this.#positionSet.add(posStr(pos));
    return pos;
  }

  #hasPosition(p: MachinePosition): boolean {
    return this.#positionSet.has(posStr(p));
  }

  #nextAvailable(): MachinePosition {
    let x = 0;
    let z = 0;
    let layer = 1;

    while (layer < 100) {
      // right
      for (let i = 0; i < layer; i++) {
        const pos = [x * CUBE_SPACING, z * CUBE_SPACING] as const;
        if (!this.#hasPosition(pos)) {
          return pos;
        }
        x += 1;
      }
      // down
      for (let i = 0; i < layer; i++) {
        const pos = [x * CUBE_SPACING, z * CUBE_SPACING] as const;
        if (!this.#hasPosition(pos)) {
          return pos;
        }
        z += 1;
      }
      layer++;
      // left
      for (let i = 0; i < layer; i++) {
        const pos = [x * CUBE_SPACING, z * CUBE_SPACING] as const;
        if (!this.#hasPosition(pos)) {
          return pos;
        }
        x -= 1;
      }
      // up
      for (let i = 0; i < layer; i++) {
        const pos = [x * CUBE_SPACING, z * CUBE_SPACING] as const;
        if (!this.#hasPosition(pos)) {
          return pos;
        }
        z -= 1;
      }
      layer++;
    }
    console.warn("No free grid positions available, returning [0, 0]");
    // Fallback if no position was found
    return [0, 0];
  }
}

export class MachinePositions {
  #clans: Record<string, ClanMachinePositions>;
  constructor() {
    const s = localStorage.getItem("machinePositions");
    if (s === null) {
      this.#clans = {};
    } else {
      try {
        const all = JSON.parse(s) as Record<
          string,
          Record<string, MachinePosition>
        >;
        this.#clans = mapObjectValues(
          all,
          ([, p]) => new ClanMachinePositions(p),
        );
      } catch (err) {
        console.error(
          "Failed to parse machinePositions from localStorage, data was corrupted, assuming no machine positions were recorded",
          err,
        );
        this.#clans = {};
      }
    }
  }
  getOrSetForClan(id: string): ClanMachinePositions {
    if (this.#clans[id]) {
      return this.#clans[id];
    }
    const p = new ClanMachinePositions({});
    this.#clans[id] = p;
    return p;
  }
}

export const machinePositions = new MachinePositions();

export type MachineMethods = {
  setMachine: SetStoreFunction<Machine>;
  activateMachine(this: void): void;
  deactivateMachine(this: void): void;
  updateMachineData(this: void, data: MachineDataChange): Promise<void>;
  installMachine(this: void, opts: InstallMachineOptions): Promise<void>;
  isMachineSSHable(this: void, ssh: MachineSSH): Promise<boolean>;
  getOrGenerateMachineHardwareReport(
    this: void,
    ssh: MachineSSH,
  ): Promise<MachineHardwareReport | null>;
  getMachineDiskTemplates(this: void): Promise<MachineDiskTemplates>;
  getMachineVarsPromptGroups(this: void): Promise<MachineVarsPromptGroups>;
  updateMachine(this: void, opts: UpdateMachineOptions): Promise<void>;
};
export type InstallMachineOptions = {
  signal?: AbortSignal;
  ssh: MachineSSH;
  diskPath: string;
  varsPromptValues: Record<string, Record<string, string>>;
  onProgress?(this: void, progress: InstallMachineProgress): void;
};
export type InstallMachineProgress =
  | "disk"
  | "varsPrompts"
  | "generators"
  | "upload-secrets"
  | "nixos-anywhere"
  | "formatting"
  | "rebooting"
  | "installing";
export type UpdateMachineOptions = {
  signal?: AbortSignal;
  ssh: MachineSSH;
  onProgress?(this: void, progress: InstallMachineProgress): void;
};
export type UpdateMachineProgress =
  | "generators"
  | "upload-secrets"
  | "nixos-anywhere"
  | "formatting"
  | "rebooting"
  | "installing";

export function createMachineMethods(
  machine: Accessor<Machine>,
  [
    machines,
    { setMachines, activateMachine, deactivateMachine, updateMachineData },
  ]: readonly [Accessor<Machines>, MachinesMethods],
  [clan]: readonly [Accessor<Clan>, ClanMethods],
  _: readonly [Clans, ClansMethods],
): MachineMethods {
  const setMachine: SetStoreFunction<Machine> = (...args: unknown[]) => {
    const m = machine();
    if (m != machines().all[m.id]) {
      throw new Error(
        `This machine does not belong to the known machines: ${m.id}`,
      );
    }
    // @ts-expect-error ...args won't infer properly for overloaded functions
    setMachines("all", m.id, ...args);
  };
  const self: MachineMethods = {
    setMachine,
    activateMachine() {
      activateMachine(machine());
    },
    deactivateMachine() {
      deactivateMachine(machine());
    },
    async updateMachineData(data) {
      await updateMachineData(machine(), data);
    },
    async installMachine(opts) {
      await api.clan.installMachine(opts, machine().id, clan().id);
    },
    async isMachineSSHable(ssh) {
      return await api.clan.isMachineSSHable(ssh);
    },
    async getOrGenerateMachineHardwareReport(ssh) {
      const report = await api.clan.getMachineHardwareReport(
        machine().id,
        clan().id,
      );
      if (report) {
        return report;
      }
      return await api.clan.generateMachineHardwareReport(
        ssh,
        machine().id,
        clan().id,
      );
    },
    async getMachineDiskTemplates() {
      const output = await api.clan.getMachineDiskTemplates(
        machine().id,
        clan().id,
      );
      const templates: MachineDiskTemplates = {
        all: mapObjectValues(output, ([id, output]) => ({
          ...output,
          id,
          placeholders: mapObjectValues(
            output.placeholders,
            ([id, output]) => ({
              ...output,
              id,
            }),
          ),
        })),
        get sorted() {
          return Object.values(this.all).sort((a, b) =>
            a.name.localeCompare(b.name),
          );
        },
      };
      return templates;
    },
    async getMachineVarsPromptGroups() {
      const output = await api.clan.getMachineVarsPromptGroups(
        machine().id,
        clan().id,
      );
      const groups: MachineVarsPromptGroups = {
        all: mapObjectValues(output, ([groupId, groupOutput]) => ({
          id: groupId,
          prompts: {
            all: mapObjectValues(groupOutput, ([promptId, promptOutput]) => ({
              ...promptOutput,
              id: promptId,
            })),
            get sorted() {
              return Object.values(this.all).sort((a, b) =>
                a.name.localeCompare(b.name),
              );
            },
          },
        })),
        get sorted() {
          return Object.values(this.all).sort((a, b) =>
            a.id.localeCompare(b.id),
          );
        },
      };
      return groups;
    },
    async updateMachine(opts) {
      await api.clan.updateMachine(opts, machine().id, clan().id);
    },
  };
  return self;
}

export function createMachineFromOutput(
  id: string,
  output: MachineOutput,
  clan: Accessor<Clan>,
): Machine {
  return {
    ...output,
    data: {
      ...output.data,
      tags: output.data.tags.slice(0),
    },
    id,
    get clan() {
      return clan();
    },
    get isActive() {
      return this.clan.machines.activeMachine?.id === this.id;
    },
    get isHighlighted() {
      return this.id in this.clan.machines.highlightedMachines;
    },
    get serviceInstances() {
      return this.clan.serviceInstances.sorted.filter((instance) => {
        return Object.entries(instance.data.roles.all).some(([, role]) => {
          const tags = new Set(role.tags);
          return (
            tags.has("all") ||
            new Set(role.machines).has(this.id) ||
            !tags.isDisjointFrom(new Set(this.data.tags))
          );
        });
      });
    },
  };
}

function posStr([x, y]: MachinePosition): string {
  return `${x},${y}`;
}
