import { Accessor } from "solid-js";
import { SetStoreFunction } from "solid-js/store";
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
  // removeMachine(): void;
};
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
    // removeClan() {
    //   removeClan(clan());
    // },
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
