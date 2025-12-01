import * as api from "@/src/api";
import {
  DataSchema,
  MachineData,
  MachineMeta,
  MachineStatus,
} from "@/src/api/clan";
import { Clan } from "./Clan";
import { Accessor, createSignal, Setter } from "solid-js";
import { createStore, SetStoreFunction } from "solid-js/store";

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

  #machines: Machine[];
  #setMachines: (machines: Machine[]) => void;
  #activeIndex: Accessor<number>;
  #setActiveIndex: Setter<number>;
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
  clan: Clan;
  #machines: MachineList;
  name: string;
  data: MachineData;
  #setData: SetStoreFunction<MachineData>;
  status: MachineStatus;
  instanceRefs: string[];
  schema: DataSchema;

  constructor(meta: MachineMeta, machines: MachineList, clan: Clan) {
    this.clan = clan;
    this.#machines = machines;
    this.name = meta.name;
    [this.data, this.#setData] = createStore(meta.data);
    this.status = meta.status;
    this.instanceRefs = meta.instanceRefs;
    this.schema = meta.schema;
  }

  get isActive() {
    return this.#machines.active === this;
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
