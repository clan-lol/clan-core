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
  useClanContext,
  useClansContext,
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

export function createMachinesStore(
  machines: Accessor<Machines>,
): [Accessor<Machines>, MachinesMethods] {
  const [clan, clanMethods] = useClanContext();
  const { setClan } = clanMethods;
  // @ts-expect-error ...args won't infer properly for overloaded functions
  const setMachines: SetStoreFunction<Machines> = (...args) => {
    // @ts-expect-error ...args won't infer properly for overloaded functions
    setClan("machines", ...args);
  };
  return [
    machines,
    machinesMethods(
      [machines, setMachines],
      [clan, clanMethods],
      useClansContext(),
    ),
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
  createMachine(id: string, data: MachineDataEntity): Promise<Machine>;
  toggleHighlightedMachines(
    items: (string | Machine)[] | string | Machine,
  ): void;
  setHighlightedMachines(items: (string | Machine)[] | string | Machine): void;
  unhighlightMachines(): void;
  machinesByTag(tag: string): Machine[];
  // removeMachine(): void;
};
function machinesMethods(
  [machines, setMachines]: [Accessor<Machines>, SetStoreFunction<Machines>],
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
      setMachines("all", machine.id, "data", d);
    },
    toggleHighlightedMachines(items) {
      if (!Array.isArray(items)) {
        return self.toggleHighlightedMachines([items]);
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
        return self.setHighlightedMachines([items]);
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
