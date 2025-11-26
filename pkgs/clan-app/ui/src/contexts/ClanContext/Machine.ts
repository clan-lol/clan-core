import * as api from "@/src/api";
import { MachineData, MachineMeta, MachineStatus } from "@/src/api/clan";
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
  #setMachines: SetStoreFunction<Machine[]>;
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

  activate(nameOrIndex: string | number): void {
    if (typeof nameOrIndex === "number") {
      this.#setActiveIndex(nameOrIndex);
      return;
    }
    for (const [i, machine] of this.#machines.entries() || []) {
      if (machine.data.name === nameOrIndex) {
        this.#setActiveIndex(i);
      }
    }
  }

  get length() {
    return this.#machines.length;
  }
  [Symbol.iterator]() {
    return this.#machines[Symbol.iterator]();
  }
  get entries() {
    return this.#machines.entries();
  }

  deactive(): void {
    this.#setActiveIndex(-1);
  }
}

export class Machine {
  clan: Clan;
  #machines: MachineList;
  data: MachineData;
  status: MachineStatus;
  instanceRefs: string[];

  constructor(meta: MachineMeta, machines: MachineList, clan: Clan) {
    this.clan = clan;
    this.#machines = machines;
    this.data = meta.data;
    this.status = meta.status;
    this.instanceRefs = meta.instanceRefs;
  }

  get isActive() {
    return this.#machines.active === this;
  }

  activate(): void {
    this.#machines.activate(this.data.name);
  }

  deactivate(): void {
    if (this.isActive) {
      this.#machines.deactive();
    }
  }
}
// export type Machine = (API["list_machines"]["return"] & {
//   status: "success";
// })["data"][string] & {
//   state: ReturnType<typeof createState>;
// };

// function createState(clanPath: string, machineName: string) {
//   return createAsync(
//     async () => await api.clan.getMachineState(clanPath, machineName),
//   );
// }

// function createTags(clanPath: string, machineName: string) {
//   return createAsync(
//     async () => await api.clan.getMachineState(clanPath, machineName),
//   );
// }

// export function createMachines(clanPath: string) {
//   return createAsync(async () =>
//     Object.fromEntries(
//       Object.entries(await api.clan.getMachines(clanPath)).map(
//         ([machineName, machine]) => {
//           return [
//             machineName,
//             {
//               ...machine,
//               state: createState(clanPath, machineName),
//               tags:
//             },
//           ];
//         },
//       ),
//     ),
//   );
// }
