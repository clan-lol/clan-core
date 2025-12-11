import { Accessor } from "solid-js";
import { produce, SetStoreFunction } from "solid-js/store";
import api from "../api";
import { Clan, ClanMethods, Clans, ClansMethods, Machine } from "..";
import { MachineData, MachineEntity, toMachine } from "./machine";
import { mapObjectValues } from "@/src/util";

export type Machines = {
  all: Record<string, Machine>;
  sorted: Machine[];
  highlightedIds: string[];
  activeId: string | null;
  readonly activeMachine: Machine | null;
};

export function createMachinesStore(
  machines: Accessor<Machines>,
  [clan, clanMethods]: readonly [Accessor<Clan>, ClanMethods],
  [clans, clansMethods]: readonly [Clans, ClansMethods],
): [Accessor<Machines>, MachinesMethods] {
  return [
    machines,
    machinesMethods(machines, [clan, clanMethods], [clans, clansMethods]),
  ];
}

export type MachinesMethods = {
  setMachines: SetStoreFunction<Machines>;
  hasMachine(item: string | Machine): boolean;
  activateMachine(item: string | Machine): Machine | null;
  deactivateMachine(item?: string | Machine): Machine | null;
  createMachine(id: string, data: MachineData): Promise<Machine>;
  machinesByTag(tag: string): Machine[];
  // removeMachine(): void;
};
function machinesMethods(
  machines: Accessor<Machines>,
  [clan, { setClan }]: readonly [Accessor<Clan>, ClanMethods],
  [clans, clansMethods]: readonly [Clans, ClansMethods],
): MachinesMethods {
  // @ts-expect-error ...args won't infer properly for overloaded functions
  const setMachines: SetStoreFunction<Machines> = (...args) => {
    // @ts-expect-error ...args won't infer properly for overloaded functions
    setClan("machines", ...args);
  };
  const self: MachinesMethods = {
    setMachines,
    hasMachine(item: string | Machine): boolean {
      let id: string;
      if (typeof item === "string") {
        id = item;
      } else {
        id = item.id;
      }
      return id in machines().all;
    },
    activateMachine(item) {
      let id: string;
      if (typeof item === "string") {
        id = item;
      } else {
        id = item.id;
      }
      const machine = machines().all[id];
      if (machine) {
        setMachines("activeId", id);
        return machine;
      }
      throw new Error(`Machine does not exist: ${id}`);
    },
    deactivateMachine(item) {
      if (!item) {
        const id = machines().activeId;
        if (!id) return null;
        return self.deactivateMachine(id);
      }
      let id: string;
      if (typeof item === "string") {
        id = item;
      } else {
        id = item.id;
      }
      if (machines().activeId === id) {
        const machine = machines().all[id];
        setMachines("activeId", null);
        return machine;
      }
      return null;
    },
    async createMachine(id: string, data: MachineData) {
      await api.clan.createMachine(id, data, clan().id);
      const machine = toMachine(
        {
          id,
          data,
          dataSchema: {},
          status: "not_installed",
        },
        clan,
      );
      setMachines(
        "all",
        produce((all) => {
          all[machine.id] = machine;
        }),
      );
      return machine;
    },
    machinesByTag(tag: string) {
      return Object.entries(machines().all)
        .filter(([, machine]) => machine.data.tags.includes(tag))
        .map(([, machine]) => machine);
    },
  };
  return self;
}

export function toMachines(
  entities: Record<string, MachineEntity>,
  clan: Accessor<Clan>,
): Machines {
  const self: Machines = {
    all: mapObjectValues(entities, ([, machine]) => toMachine(machine, clan)),
    get sorted() {
      return Object.values(this.all).sort((a, b) => {
        return a.id.localeCompare(b.id);
      });
    },
    highlightedIds: [],
    activeId: null,
    get activeMachine() {
      return this.activeId ? this.all[this.activeId] : null;
    },
  };
  return self;
}
