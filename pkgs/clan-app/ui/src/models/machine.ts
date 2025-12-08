import { JSONSchema } from "json-schema-typed/draft-2020-12";
import { Accessor } from "solid-js";
import { produce, reconcile, SetStoreFunction } from "solid-js/store";
import api from "./api";
import { Clan, Clans, ClanMethods, ClansMethods } from "./clan";
import { ServiceInstance } from "./service";
import { DataSchema } from ".";

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

export type Machines = {
  all: Machine[];
  activeIndex: number;
  readonly activeMachine: Machine | undefined;
};

export function createMachinesStore(
  machines: Accessor<Machines>,
  clanValue: readonly [Accessor<Clan>, ClanMethods],
  clansValue: readonly [Clans, ClansMethods],
): [Accessor<Machines>, MachinesMethods] {
  return [machines, machinesMethods(machines, clanValue, clansValue)];
}

export type MachinesMethods = {
  setMachines: SetStoreFunction<Machines>;
  machineIndex(item: string | Machine): number;
  hasMachine(item: string | Machine): boolean;
  activateMachine(item: number | Machine): Machine | undefined;
  deactivateMachine(item?: number | Machine): Machine | undefined;
  addMachine(entity: NewMachineEntity): Promise<Machine>;
  // removeMachine(): void;
};
function machinesMethods(
  machines: Accessor<Machines>,
  [clan, { setClan }]: readonly [Accessor<Clan>, ClanMethods],
  clansValue: readonly [Clans, ClansMethods],
): MachinesMethods {
  // @ts-expect-error ...args won't infer properly for overloaded functions
  const setMachines: SetStoreFunction<Machines> = (...args) => {
    // @ts-expect-error ...args won't infer properly for overloaded functions
    setClan("machines", ...args);
  };
  const self: MachinesMethods = {
    setMachines,
    machineIndex(item: string | Machine): number {
      if (typeof item === "string") {
        for (const [i, machine] of machines().all.entries()) {
          if (machine.id === item) {
            return i;
          }
        }
        return -1;
      }
      return self.machineIndex(item.id);
    },
    hasMachine(item: string | Machine): boolean {
      return self.machineIndex(item) !== -1;
    },
    activateMachine(item) {
      if (typeof item === "number") {
        const i = item;
        if (i < 0 || i >= machines().all.length) {
          throw new Error(`activateMachine called with invalid index: ${i}`);
        }
        if (machines().activeIndex === i) return;

        const machine = machines().all[i];
        setMachines("activeIndex", i);
        return machine;
      }
      return self.activateMachine(item.index);
    },
    deactivateMachine(item) {
      if (typeof item === "number") {
        if (item === machines().activeIndex) {
          setMachines("activeIndex", -1);
          return machines().all[item];
        }
        return;
      }
      if (!item) {
        setMachines("activeIndex", -1);
        return;
      }
      return self.deactivateMachine(item.index);
    },
    async addMachine(newEntity) {
      const entity = await api.clan.createMachine(clan().id, newEntity);
      const machine = toMachine(entity, clan().id, clansValue);
      setMachines(
        "all",
        produce((all) => {
          all.push(machine);
        }),
      );
      return machine;
    },
  };
  return self;
}

export type MachineEntity = {
  readonly id: string;
  readonly data: MachineData;
  readonly dataSchema: DataSchema;
  readonly status: MachineStatus;
  readonly position: readonly [number, number];
};
export type Machine = Omit<MachineEntity, "data"> & {
  readonly clan: Clan;
  data: MachineData;
  position: readonly [number, number];
  readonly index: number;
  readonly isActive: boolean;
  readonly serviceInstances: ServiceInstance[];
};
export type NewMachineEntity = Pick<MachineEntity, "id" | "data"> & {
  readonly position: readonly [number, number];
};
export type PersistMachine = {
  position: [number, number];
};

export type MachineData = {
  // TODO: don't use nested fields, it makes updating data much more complex
  // because we need to deal with deep merging
  deploy?: {
    buildHost?: string;
    targetHost?: string;
  };
  description?: string;
  icon?: string;
  installedAt?: number;
  machineClass: "nixos" | "darwin";
  tags: string[];
};

export type MachineStatus =
  | "not_installed"
  | "offline"
  | "out_of_sync"
  | "online";

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

export function toMachines(
  entities: MachineEntity[],
  clanId: string,
  clansValue: readonly [Clans, ClansMethods],
): Machines {
  const self: Machines = {
    all: entities.map((machine) => toMachine(machine, clanId, clansValue)),
    activeIndex: -1,
    get activeMachine(): Machine | undefined {
      return this.activeIndex === -1 ? undefined : this.all[this.activeIndex];
    },
  };
  return self;
}

function toMachine(
  machine: MachineEntity,
  clanId: string,
  clansValue: readonly [Clans, ClansMethods],
): Machine {
  const [clans, { clanIndex }] = clansValue;
  return {
    ...machine,
    get clan(): Clan {
      const i = clanIndex(clanId);
      if (i === -1) {
        throw new Error(`Clan does not exist: ${clanId}`);
      }
      return clans.all[i] as Clan;
    },
    get index(): number {
      const machines = this.clan.machines.all;
      if (!machines) return -1;
      for (const [i, machine] of machines.entries()) {
        if (machine.id === this.id) {
          return i;
        }
      }
      return -1;
    },
    get isActive(): boolean {
      return this.clan.machines.activeMachine?.id === this.id;
    },
    get serviceInstances(): ServiceInstance[] {
      return (
        this.clan.serviceInstances.all.filter((instance) => {
          return instance.roles.some((role) => {
            const tags = new Set(role.tags);
            return (
              tags.has("all") ||
              new Set(role.machines).has(this.id) ||
              !tags.isDisjointFrom(new Set(this.data.tags))
            );
          });
        }) || []
      );
    },
  };
}

function posStr([x, y]: readonly [number, number]): string {
  return `${x},${y}`;
}
