import { Accessor } from "solid-js";
import { produce, SetStoreFunction } from "solid-js/store";
import api from "../api";
import {
  Clan,
  ClanMethods,
  Clans,
  MachineDataEntity,
  ClansMethods,
  Machine,
} from "..";
import { MachineData, MachineEntity, createMachine } from "./machine";
import { mapObjectValues } from "@/src/util";

export type Machines = {
  all: Record<string, Machine>;
  readonly sorted: Machine[];
  // Idealy this should be Set<string>, but solidjs' produce function
  // doesn't work with Sets or Maps
  highlightedMachines: Record<string, Machine>;
  activeMachine: Machine | null;
};

export type MachinesMethods = {
  setMachines: SetStoreFunction<Machines>;
  activateMachine(this: void, item: Machine | string): Machine | null;
  deactivateMachine(this: void): void;
  deactivateMachine(this: void, item: Machine | string): Machine | null;
  updateMachineData(
    this: void,
    item: Machine | string,
    data: Partial<MachineData>,
  ): Promise<void>;
  createMachine(this: void, id: string, data: MachineData): Promise<Machine>;
  toggleHighlightedMachines(
    this: void,
    items: (string | Machine)[] | string | Machine,
  ): void;
  setHighlightedMachines(
    this: void,
    items: (string | Machine)[] | string | Machine,
  ): void;
  unhighlightMachines(this: void): void;
  deleteMachine(this: void, item: Machine | string): Promise<void>;
  machinesByTag(this: void, tag: string): Machine[];
};
export function createMachinesMethods(
  machines: Accessor<Machines>,
  [clan, { setClan }]: readonly [Accessor<Clan>, ClanMethods],
  _: readonly [Clans, ClansMethods],
): MachinesMethods {
  const setMachines: SetStoreFunction<Machines> = (...args: unknown[]) => {
    // @ts-expect-error ...args won't infer properly for overloaded functions
    setClan("machines", ...args);
  };

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
      return;
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
      const machine = createMachine(
        id,
        {
          data: data as MachineDataEntity,
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
      //
      // FIXME: assign deploy is unecessary, currently it's only to make
      // typescript happy
      const d = { ...machine.data, ...data, deploy: machine.data.deploy };
      await api.clan.updateMachineData(machine.id, clan().id, d);
      setMachines("all", machine.id, "data", d);
    },
    toggleHighlightedMachines(items) {
      if (!Array.isArray(items)) {
        self.toggleHighlightedMachines([items]);
        return;
      }

      const togglingMachines = Object.fromEntries(
        items.map((item) => {
          const machine = getMachine(item);
          return [machine.id, machine];
        }),
      );
      const oldHighlighted = machines().highlightedMachines;
      const newHighlighted: Record<string, Machine> = {};
      for (const [id, machine] of Object.entries(oldHighlighted)) {
        if (!(id in togglingMachines)) {
          newHighlighted[id] = machine;
        }
      }
      for (const [id, machine] of Object.entries(togglingMachines)) {
        if (!(id in oldHighlighted)) {
          newHighlighted[id] = machine;
        }
      }
      setMachines(
        produce((machines) => (machines.highlightedMachines = newHighlighted)),
      );
    },
    setHighlightedMachines(items) {
      if (!Array.isArray(items)) {
        self.setHighlightedMachines([items]);
        return;
      }
      const highlighted = Object.fromEntries(
        items.map((item) => {
          const machine = getMachine(item);
          return [machine.id, machine];
        }),
      );
      setMachines(
        produce((machines) => (machines.highlightedMachines = highlighted)),
      );
    },
    unhighlightMachines() {
      setMachines(produce((machines) => (machines.highlightedMachines = {})));
    },
    async deleteMachine(item) {
      const machine = getMachine(item);
      await api.clan.deleteMachine(machine.id, clan().id);
      setMachines(
        produce((machines) => {
          if (machines.activeMachine?.id === machine.id) {
            machines.activeMachine = null;
          }
          /* eslint-disable @typescript-eslint/no-dynamic-delete */
          delete machines.highlightedMachines[machine.id];
          /* eslint-disable @typescript-eslint/no-dynamic-delete */
          delete machines.all[machine.id];
        }),
      );
    },
    machinesByTag(tag: string) {
      return Object.entries(machines().all)
        .filter(([, machine]) => machine.data.tags.includes(tag))
        .map(([, machine]) => machine);
    },
  };
  return self;
}

export function createMachines(
  entities: Record<string, MachineEntity>,
  clan: Accessor<Clan>,
): Machines {
  const self: Machines = {
    all: mapObjectValues(entities, ([id, machine]) =>
      createMachine(id, machine, clan),
    ),
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
