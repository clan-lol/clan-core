import { Accessor } from "solid-js";
import { produce, reconcile, SetStoreFunction } from "solid-js/store";
import api from "../api";
import {
  Clan,
  ClanMethods,
  Clans,
  MachineEntityData,
  ClansMethods,
  Machine,
} from "..";
import { MachineData, MachineEntity, toMachine } from "./machine";
import { mapObject, mapObjectValues } from "@/src/util";

export type Machines = {
  all: Record<string, Machine>;
  readonly sorted: Machine[];
  // Idealy this should be Set<string>, but solidjs' produce function
  // doesn't work with Sets or Maps
  highlightedMachines: Record<string, Machine>;
  activeMachine: Machine | null;
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
  activateMachine(item: Machine | string): Machine | null;
  deactivateMachine(): void;
  deactivateMachine(item: Machine | string): Machine | null;
  updateMachineData(
    item: Machine | string,
    data: Partial<MachineData>,
  ): Promise<void>;
  createMachine(id: string, data: MachineEntityData): Promise<Machine>;
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
  function getMachine(item: Machine | string): Machine {
    if (typeof item === "string") {
      const id = item;
      const machine = machines().all[id];
      if (!machine) {
        throw new Error(`Machine does not exist: ${id}`);
      }
      return machine;
    }
    const machine = item;
    if (machine !== machines().all[machine.id]) {
      throw new Error(
        `This machine does not belong to the known machines: ${machine.id}`,
      );
    }
    return machine;
  }

  function deactivateMachine(): void;
  function deactivateMachine(item: Machine | string): Machine | null;
  function deactivateMachine(item?: Machine | string): void | Machine | null {
    if (!item) {
      const machine = machines().activeMachine;
      if (!machine) {
        return null;
      }
      setMachines(
        produce((machines) => {
          machines.activeMachine = null;
        }),
      );
      return machine;
    }
    const machine = getMachine(item);
    if (machine !== machines().activeMachine) {
      return null;
    }
    setMachines(
      produce((machines) => {
        machines.activeMachine = null;
      }),
    );
    return machine;
  }
  // @ts-expect-error ...args won't infer properly for overloaded functions
  const setMachines: SetStoreFunction<Machines> = (...args) => {
    // @ts-expect-error ...args won't infer properly for overloaded functions
    setClan("machines", ...args);
  };
  const self: MachinesMethods = {
    setMachines,
    activateMachine(item) {
      const machine = getMachine(item);
      if (machines().activeMachine === machine) {
        return null;
      }
      setMachines(
        produce((machines) => {
          machines.activeMachine = machine;
        }),
      );
      return machine;
    },
    deactivateMachine,
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
    async updateMachineData(item, data) {
      const machine = getMachine(item);
      if (data.position) {
        setMachines("all", machine.id, "data", "position", data.position);
        if (Object.keys(data).length == 1) {
          return;
        }
      }
      // TODO: Use partial update once supported by backend and solidjs
      // https://github.com/solidjs/solid/issues/2475
      const d = { ...machine.data, ...data };
      await api.clan.updateMachineData(machine.id, clan().id, d);
      setMachines("all", machine.id, "data", reconcile(d));
    },
    highlightMachines(items) {
      if (!Array.isArray(items)) {
        return self.highlightMachines([items]);
      }
      setMachines(
        "highlightedMachines",
        produce((machines) =>
          Object.assign(
            machines,
            Object.fromEntries(
              items.map((item) => {
                const machine = getMachine(item);
                return [machine.id, machine];
              }),
            ),
          ),
        ),
      );
    },
    unhighlightMachines(items) {
      if (!items) {
        setMachines("highlightedMachines", {});
        return;
      }
      if (!Array.isArray(items)) {
        return self.unhighlightMachines([items]);
      }
      const unhighlighted = new Set(
        items.map((item) => getMachine(item)).map((machine) => machine.id),
      );
      // Use delete to remove the unhighlighted is more intuitive but delete is
      // slow in JS engines and we also need to use batch to ensure multiple
      // deletes only result in one rendering
      const highlighted = mapObject(
        machines().highlightedMachines,
        ([id, machine]) => {
          if (unhighlighted.has(id)) {
            return [];
          }
          return [id, machine];
        },
      );
      setMachines("highlightedMachines", reconcile(highlighted));
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
    highlightedMachines: {},
    activeMachine: null,
  };
  return self;
}
