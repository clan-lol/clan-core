import { Accessor, batch } from "solid-js";
import { produce, reconcile, SetStoreFunction } from "solid-js/store";
import api from "../api";
import { Clan, ClanMethods, Clans, ClansMethods, Machine } from "..";
import { MachineData, MachineEntity, toMachine } from "./machine";
import { isSamePosition, mapObjectValues } from "@/src/util";

export type Machines = {
  all: Record<string, Machine>;
  sorted: Machine[];
  // Idealy this should be Set<string>, but solidjs' produce function
  // doesn't work with Sets or Maps
  highlightedIds: Record<string, true | undefined>;
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
  getMachine(item: string): Machine;
  activateMachine(item: string | Machine): Machine | null;
  deactivateMachine(item?: string | Machine): Machine | null;
  createMachine(id: string, data: MachineData): Promise<Machine>;
  setMachinePosition(
    item: string | Machine,
    pos: readonly [number, number],
  ): void;
  isMachineAtPosition(
    item: string | Machine,
    pos: readonly [number, number],
  ): boolean;
  highlightMachines(items: (string | Machine)[] | string | Machine): void;
  unhighlightMachines(items?: (string | Machine)[] | string | Machine): void;
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
    getMachine(id) {
      const machine = machines().all[id];
      if (machine) {
        return machine;
      }
      throw new Error(`Machine does not exist: ${id}`);
    },
    activateMachine(item) {
      const id = getMachineId(item);
      const machine = self.getMachine(id);
      setMachines("activeId", id);
      return machine;
    },
    deactivateMachine(item) {
      if (!item) {
        const id = machines().activeId;
        if (!id) return null;
        return self.deactivateMachine(id);
      }
      const id = getMachineId(item);
      const machine = self.getMachine(id);
      if (machine.id === machines().activeId) {
        setMachines("activeId", null);
        return machine;
      }
      return null;
    },
    async createMachine(id, data) {
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
    setMachinePosition(item, pos) {
      const id = getMachineId(item);
      // Ensure the id exists
      self.getMachine(id);
      setMachines("all", id, "data", "position", pos);
    },
    isMachineAtPosition(item, pos) {
      const id = getMachineId(item);
      const machine = self.getMachine(id);
      return isSamePosition(machine.data.position, pos);
    },
    highlightMachines(items) {
      if (!Array.isArray(items)) {
        return self.highlightMachines([items]);
      }
      batch(() => {
        for (const item of items) {
          const id = getMachineId(item);
          // Ensure the id exists
          self.getMachine(id);
          setMachines(
            "highlightedIds",
            produce((ids) => (ids[id] = true)),
          );
        }
      });
    },
    unhighlightMachines(items) {
      if (!items) {
        setMachines("highlightedIds", reconcile({}));
        return;
      }
      if (!Array.isArray(items)) {
        return self.unhighlightMachines([items]);
      }
      batch(() => {
        for (const item of items) {
          const id = getMachineId(item);
          // Ensure the id exists
          self.getMachine(id);
          setMachines(
            "highlightedIds",
            produce((ids) => (ids[id] = undefined)),
          );
        }
      });
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
    highlightedIds: {},
    activeId: null,
    get activeMachine() {
      return this.activeId ? this.all[this.activeId] : null;
    },
  };
  return self;
}

function getMachineId(item: string | Machine): string {
  if (typeof item === "string") {
    return item;
  }
  return item.id;
}
