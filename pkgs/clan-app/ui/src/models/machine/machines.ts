import { Accessor } from "solid-js";
import { produce, SetStoreFunction } from "solid-js/store";
import api from "../api";
import { Clan, ClanMethods, Clans, ClansMethods, Machine } from "..";
import { MachineEntity, NewMachineEntity, toMachine } from "./machine";

export type Machines = {
  all: Machine[];
  activeIndex: number;
  readonly activeMachine: Machine | undefined;
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
  machineIndex(item: string | Machine): number;
  hasMachine(item: string | Machine): boolean;
  activateMachine(item: number | Machine): Machine | undefined;
  deactivateMachine(item?: number | Machine): Machine | undefined;
  addMachine(entity: NewMachineEntity): Promise<Machine>;
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
      const machine = toMachine(entity, clan);
      setMachines(
        "all",
        produce((all) => {
          all.push(machine);
        }),
      );
      return machine;
    },
    machinesByTag(tag: string) {
      return machines().all.filter((machine) =>
        machine.data.tags.includes(tag),
      );
    },
  };
  return self;
}

export function toMachines(
  entities: MachineEntity[],
  clan: Accessor<Clan>,
): Machines {
  const self: Machines = {
    all: entities.map((machine) => toMachine(machine, clan)),
    activeIndex: -1,
    get activeMachine(): Machine | undefined {
      return this.activeIndex === -1 ? undefined : this.all[this.activeIndex];
    },
  };
  return self;
}
