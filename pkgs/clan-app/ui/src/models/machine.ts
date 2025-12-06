import { JSONSchema } from "json-schema-typed/draft-2020-12";
import { Accessor, createSignal, Setter } from "solid-js";
import { createStore, reconcile, SetStoreFunction } from "solid-js/store";
import api from "./api";
import { Clan, Clans, ClanSetters, ClansSetters } from "./clan";
import { Service, ServiceInstance } from "./Service";
import { DataSchema } from ".";

export type Machines = {
  all: Machine[];
  activeIndex: number;
  readonly activeMachine: Machine | undefined;
};

export function createMachinesStore(
  machines: Accessor<Machines>,
  [clan, clanSetters]: [Accessor<Clan>, ClanSetters],
  [clans, clansSetters]: [Clans, ClansSetters],
): [Accessor<Machines>, MachinesSetters] {
  return [
    machines,
    machinesSetters(machines, [clan, clanSetters], [clans, clansSetters]),
  ];
}

export type MachinesSetters = {
  setMachines: SetStoreFunction<Machines>;
  activateMachine(item: number | Machine): Machine | undefined;
  deactivateMachine(item?: number | Machine): Machine | undefined;
  // addMachine(entity: MachineNewEntity): Promise<MachineEntity>;
  // removeMachine(): void;
};
function machinesSetters(
  machines: Accessor<Machines>,
  [clan, { setClan }]: [Accessor<Clan>, ClanSetters],
  [clans]: [Clans, ClansSetters],
): MachinesSetters {
  // @ts-expect-error ...args won't infer properly for overloaded functions
  const setMachines: SetStoreFunction<Machines> = (...args) => {
    // @ts-expect-error ...args won't infer properly for overloaded functions
    setClan("machines", ...args);
  };
  const self: MachinesSetters = {
    setMachines,
    activateMachine(item) {
      if (typeof item === "number") {
        const machine = machines().all[item];
        setMachines("activeIndex", item);
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
  };
  return self;
}

export type MachineEntity = {
  readonly id: string;
  readonly data: MachineData;
  readonly dataSchema: DataSchema;
  readonly status: MachineStatus;
  readonly serviceInstances: string[];
};
export type Machine = Omit<MachineEntity, "data"> & {
  data: MachineData;
  readonly index: number;
  readonly isActive: boolean;
};
export type MachineNewEntity = Pick<MachineEntity, "id" | "data">;

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
  machinesValue: [Accessor<Machines>, MachinesSetters],
  clanValue: [Accessor<Clan>, ClanSetters],
  clansValue: [Clans, ClansSetters],
): [Accessor<Machine>, MachineSetters] {
  return [
    machine,
    machineSetters(machine, machinesValue, clanValue, clansValue),
  ];
}

export type MachineSetters = {
  setMachine: SetStoreFunction<Machine>;
  activateMachine(): void;
  deactivateMachine(): void;
  updateMachineData(data: Partial<MachineData>): Promise<void>;
  // removeMachine(): void;
};
function machineSetters(
  machine: Accessor<Machine>,
  [machines, { setMachines, activateMachine, deactivateMachine }]: [
    Accessor<Machines>,
    MachinesSetters,
  ],
  [clan]: [Accessor<Clan>, ClanSetters],
  [clans]: [Clans, ClansSetters],
): MachineSetters {
  // @ts-expect-error ...args won't infer properly for overloaded functions
  const setMachine: SetStoreFunction<Machine> = (...args) => {
    // @ts-expect-error ...args won't infer properly for overloaded functions
    setMachines("all", machine().index, ...args);
  };
  const self: MachineSetters = {
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
