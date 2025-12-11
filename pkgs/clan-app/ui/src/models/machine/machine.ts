import { Accessor } from "solid-js";
import { reconcile, SetStoreFunction } from "solid-js/store";
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

export type MachineEntity = {
  readonly id: string;
  readonly data: MachineData;
  readonly dataSchema: DataSchema;
  readonly status: MachineStatus;
};
export type Machine = {
  readonly clan: Clan;
  readonly id: string;
  data: MachineData;
  readonly dataSchema: DataSchema;
  readonly status: MachineStatus;
  readonly isActive: boolean;
  readonly serviceInstances: ServiceInstance[];
};

export type MachineData = {
  deploy: {
    buildHost?: string;
    targetHost?: string;
  };
  description?: string;
  machineClass: "nixos" | "darwin";
  tags: string[];
  position: readonly [number, number];
};

export type MachineStatus =
  | "not_installed"
  | "offline"
  | "out_of_sync"
  | "online";

const CUBE_SPACING = 1;
export class MachinePositions {
  #all: Record<string, readonly [number, number]>;
  #set: Set<string>;
  constructor(all: Record<string, readonly [number, number]>) {
    this.#all = all;
    this.#set = new Set(Object.values(all).map(posStr));
  }
  getOrSetPosition(machineId: string): readonly [number, number] {
    if (this.#all[machineId]) {
      return this.#all[machineId];
    }
    const pos = this.#nextAvailable();
    this.#all[machineId] = pos;
    this.#set.add(posStr(pos));
    return pos;
  }

  #hasPosition(p: readonly [number, number]): boolean {
    return this.#set.has(posStr(p));
  }

  #nextAvailable(): readonly [number, number] {
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
  const all = JSON.parse(s) as Record<
    string,
    Record<string, readonly [number, number]>
  >;
  return Object.fromEntries(
    Object.entries(all).map(([clanId, p]) => [clanId, new MachinePositions(p)]),
  );
})();

export function createMachineStore(
  machine: Accessor<Machine>,
  machinesValue: readonly [Accessor<Machines>, MachinesMethods],
  clanValue: readonly [Accessor<Clan>, ClanMethods],
  clansValue: readonly [Clans, ClansMethods],
): readonly [Accessor<Machine>, MachineMethods] {
  return [
    machine,
    machineMethods(machine, machinesValue, clanValue, clansValue),
  ];
}

export type MachineMethods = {
  setMachine: SetStoreFunction<Machine>;
  activateMachine(): void;
  deactivateMachine(): void;
  updateMachineData(data: Partial<MachineData>): Promise<void>;
  // removeMachine(): void;
};
function machineMethods(
  machine: Accessor<Machine>,
  [machines, { setMachines, activateMachine, deactivateMachine }]: readonly [
    Accessor<Machines>,
    MachinesMethods,
  ],
  [clan]: readonly [Accessor<Clan>, ClanMethods],
  [clans]: readonly [Clans, ClansMethods],
): MachineMethods {
  // @ts-expect-error ...args won't infer properly for overloaded functions
  const setMachine: SetStoreFunction<Machine> = (...args) => {
    // @ts-expect-error ...args won't infer properly for overloaded functions
    setMachines("all", machine().index, ...args);
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
      // TODO: Use partial update once supported by backend and solidjs
      // https://github.com/solidjs/solid/issues/2475
      const d = { ...machine().data, ...data };
      await api.clan.updateMachineData(machine().id, clan().id, d);
      setMachine("data", reconcile(d));
    },
    // removeClan() {
    //   removeClan(clan());
    // },
  };
  return self;
}

export function toMachine(
  machine: MachineEntity,
  clan: Accessor<Clan>,
): Machine {
  return {
    ...machine,
    get clan() {
      return clan();
    },
    get isActive() {
      return this.clan.machines.activeMachine?.id === this.id;
    },
    get serviceInstances() {
      return this.clan.serviceInstances.all.filter((instance) => {
        return Object.entries(instance.data.roles).some(([, role]) => {
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

function posStr([x, y]: readonly [number, number]): string {
  return `${x},${y}`;
}
