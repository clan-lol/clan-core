import { JSONSchema } from "json-schema-typed/draft-2020-12";
import { Accessor, createSignal, Setter } from "solid-js";
import { createStore, SetStoreFunction } from "solid-js/store";
import api from "./api";
import { Clan } from "./clan";
import { Service, ServiceInstance } from "./Service";

export class MachineList {
  static async get(clan: Clan): Promise<MachineList> {
    const list = new MachineList([]);
    const machines = Object.entries(await api.clan.getMachines(clan.id)).map(
      ([, meta]) => {
        return new Machine(meta, list, clan);
      },
    );
    list.#setMachines(machines);
    return list;
  }

  readonly #machines: Machine[];
  readonly #setMachines: (machines: Machine[]) => void;
  readonly #activeIndex: Accessor<number>;
  readonly #setActiveIndex: Setter<number>;

  private constructor(machines: Machine[]) {
    [this.#machines, this.#setMachines] = createStore(machines);
    [this.#activeIndex, this.#setActiveIndex] = createSignal(-1);
  }

  get active(): Machine | null {
    return this.#activeIndex() === -1
      ? null
      : this.#machines[this.#activeIndex()] || null;
  }

  activate(name: string): void {
    for (const [i, machine] of this.#machines.entries() || []) {
      if (machine.name === name) {
        this.#setActiveIndex(i);
      }
    }
  }

  get length(): number {
    return this.#machines.length;
  }
  [Symbol.iterator](): ArrayIterator<Machine> {
    return this.#machines[Symbol.iterator]();
  }
  entries(): ArrayIterator<[number, Machine]> {
    return this.#machines.entries();
  }

  deactivate(): void {
    this.#setActiveIndex(-1);
  }
}

export class Machine {
  readonly clan: Clan;
  readonly #machines: MachineList;
  readonly name: string;
  readonly data: MachineData;
  readonly #setData: SetStoreFunction<MachineData>;
  readonly status: MachineStatus;
  readonly serviceInstances: string[];
  readonly schema: DataSchema;

  constructor(meta: MachineMeta, machines: MachineList, clan: Clan) {
    this.clan = clan;
    this.#machines = machines;
    this.name = meta.name;
    [this.data, this.#setData] = createStore(meta.data);
    this.status = meta.status;
    this.serviceInstances = meta.serviceInstances;
    this.schema = meta.schema;
  }

  get isActive() {
    return this.#machines.active?.name === this.name;
  }

  activate(): void {
    this.#machines.activate(this.name);
  }

  deactivate(): void {
    if (this.isActive) {
      this.#machines.deactivate();
    }
  }

  async updateData(data: MachineData) {
    await api.clan.updateMachineData(this.clan.id, this.name, data);
    this.#setData(data);
  }
}

export type MachineData = {
  // TODO: don't use nested fields, it makes updating data much more complex
  // because we need to deal with deep merging and check if the whole object
  // is missing or not
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

export type MachineEntity = {
  // TODO: name should be renamed to id
  name: string;
  data: MachineData;
  dataSchema: JSONSchema;
  serviceInstances: string[];
  status: MachineStatus;
};

export type MachineStatus =
  | "not_installed"
  | "offline"
  | "out_of_sync"
  | "online";
