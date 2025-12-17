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
  useClanContext,
  useClansContext,
  useMachinesContext,
} from "..";
import { mapObjectValues } from "@/src/util";

export type MachineEntity = {
  readonly data: MachineDataEntity;
  readonly dataSchema: DataSchema;
  readonly status: MachineStatus;
};
export type MachineDataEntity = {
  deploy: {
    buildHost?: string;
    targetHost?: string;
  };
  description?: string;
  machineClass: "nixos" | "darwin";
  tags: string[];
  position: MachinePosition;
};
export type MachinePosition = readonly [number, number];

export type Machine = Omit<MachineEntity, "data"> & {
  readonly clan: Clan;
  readonly id: string;
  data: MachineData;
  readonly isActive: boolean;
  readonly isHighlighted: boolean;
  readonly serviceInstances: ServiceInstance[];
};
export type MachineData = MachineDataEntity;

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

export type MachineHardwareReportEntity = {
  readonly type: "nixos-facter" | "nixos-generate-config";
};

export type MachineHardwareReport = MachineHardwareReportEntity;

export type MachineDiskTemplatesEntity = Record<
  string,
  MachineDiskTemplateEntity
>;
export type MachineDiskTemplateEntity = {
  readonly name: string;
  readonly description: string;
  readonly placeholders: Record<string, MachineDiskTemplatePlaceHolderEntity>;
};
export type MachineDiskTemplatePlaceHolderEntity = {
  readonly name: string;
  readonly values: string[];
  readonly required: boolean;
};

export type MachineDiskTemplates = {
  all: Record<string, MachineDiskTemplate>;
  sorted: MachineDiskTemplate[];
};
export type MachineDiskTemplate = Omit<
  MachineDiskTemplateEntity,
  "placeholders"
> & {
  readonly id: string;
  readonly placeholders: Record<string, MachineDiskTemplatePlaceHolder>;
};
export type MachineDiskTemplatePlaceHolder =
  MachineDiskTemplatePlaceHolderEntity & {
    readonly id: string;
  };

export type MachineVarsPromptGroupsEntity = Record<
  string,
  MachineVarsPromptsEntity
>;
export type MachineVarsPromptsEntity = Record<string, MachineVarsPromptEntity>;
export type MachineVarsPromptEntity = {
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
export type MachineVarsPrompt = MachineVarsPromptEntity & {
  readonly id: string;
};

const CUBE_SPACING = 1;
export class MachinePositions {
  #all: Record<string, MachinePosition>;
  #set: Set<string>;
  constructor(all: Record<string, MachinePosition>) {
    this.#all = all;
    this.#set = new Set(Object.values(all).map(posStr));
  }
  getOrSetPosition(machineId: string): MachinePosition {
    if (this.#all[machineId]) {
      return this.#all[machineId];
    }
    const pos = this.#nextAvailable();
    this.#all[machineId] = pos;
    this.#set.add(posStr(pos));
    return pos;
  }

  #hasPosition(p: MachinePosition): boolean {
    return this.#set.has(posStr(p));
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

export const machinePositions: Record<string, MachinePositions> = (() => {
  const s = localStorage.getItem("machinePositions");
  if (s === null) {
    return {};
  }
  const all = JSON.parse(s) as Record<string, Record<string, MachinePosition>>;
  return mapObjectValues(all, ([clanId, p]) => new MachinePositions(p));
})();

export function createMachineStore(
  machine: Accessor<Machine>,
): readonly [Accessor<Machine>, MachineMethods] {
  return [
    machine,
    createMachineMethods(
      machine,
      useMachinesContext(),
      useClanContext(),
      useClansContext(),
    ),
  ];
}

export type MachineMethods = {
  setMachine: SetStoreFunction<Machine>;
  activateMachine(): void;
  deactivateMachine(): void;
  updateMachineData(data: Partial<MachineData>): Promise<void>;
  installMachine(opts: InstallMachineOptions): Promise<void>;
  isMachineSSHable(ssh: MachineSSH): Promise<boolean>;
  getOrGenerateMachineHardwareReport(
    ssh: MachineSSH,
  ): Promise<MachineHardwareReport | null>;
  getMachineDiskTemplates(): Promise<MachineDiskTemplates>;
  getMachineVarsPromptGroups(): Promise<MachineVarsPromptGroups>;
  updateMachine(opts: UpdateMachineOptions): Promise<void>;
};
export type InstallMachineOptions = {
  signal?: AbortSignal;
  ssh: MachineSSH;
  diskPath: string;
  varsPromptValues: Record<string, Record<string, string>>;
  onProgress?(progress: InstallMachineProgress): void;
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
  onProgress?(progress: InstallMachineProgress): void;
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
  [clans]: readonly [Clans, ClansMethods],
): MachineMethods {
  // @ts-expect-error ...args won't infer properly for overloaded functions
  const setMachine: SetStoreFunction<Machine> = (...args) => {
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
      const entity = await api.clan.getMachineDiskTemplates(
        machine().id,
        clan().id,
      );
      const templates: MachineDiskTemplates = {
        all: mapObjectValues(entity, ([id, entity]) => ({
          ...entity,
          id,
          placeholders: mapObjectValues(
            entity.placeholders,
            ([id, entity]) => ({
              ...entity,
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
      const entity = await api.clan.getMachineVarsPromptGroups(
        machine().id,
        clan().id,
      );
      const groups: MachineVarsPromptGroups = {
        all: mapObjectValues(entity, ([groupId, groupEntity]) => ({
          id: groupId,
          prompts: {
            all: mapObjectValues(groupEntity, ([promptId, promptEntity]) => ({
              ...promptEntity,
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

export function createMachine(
  id: string,
  entity: MachineEntity,
  clan: Accessor<Clan>,
): Machine {
  return {
    ...entity,
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
