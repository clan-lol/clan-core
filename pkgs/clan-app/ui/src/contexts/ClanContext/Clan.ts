import * as api from "@/src/api";
import { AccessorWithLatest, createAsync } from "@solidjs/router";
import { MachineList } from "./Machine";
import { ClanData, ClanMeta } from "@/src/api/clan";
import { createStore, SetStoreFunction } from "solid-js/store";
import { Accessor, createSignal, Setter } from "solid-js";
import { makePersisted } from "@solid-primitives/storage";

export class ClanList {
  static #setIds: SetStoreFunction<string[]>;
  static #shared: ClanList;
  static async get(): Promise<ClanList> {
    if (this.#shared) {
      return this.#shared;
    }

    const [ids, setIds] = makePersisted(createStore<string[]>([]), {
      name: "clanIds",
    });
    this.#setIds = setIds;

    const list = new ClanList([]);
    const clans = (await api.clan.getClans(ids)).map(
      (data) => new Clan(data, list),
    );
    list.#setClans(clans);
    this.#shared = list;
    return list;
  }

  #clans: Clan[];
  #setClans: SetStoreFunction<Clan[]>;
  #activeIndex: Accessor<number>;
  #setActiveIndex: Setter<number>;

  private constructor(clans: Clan[]) {
    [this.#clans, this.#setClans] = createStore(clans);
    [this.#activeIndex, this.#setActiveIndex] = makePersisted(
      createSignal(-1),
      {
        name: "activeClanIndex",
      },
    );
  }
  get length() {
    return this.#clans.length;
  }
  [Symbol.iterator]() {
    return this.#clans[Symbol.iterator]();
  }
  get entries() {
    return this.#clans.entries();
  }

  get active(): Clan | null {
    const i = this.#activeIndex();
    return i === -1 ? null : this.#clans[i] || null;
  }

  activate(idOrIndex: string | number): void {
    if (typeof idOrIndex === "number") {
      this.#setActiveIndex(idOrIndex);
      return;
    }
    for (const [i, clan] of this.#clans.entries()) {
      if (clan.id === idOrIndex) {
        this.#setActiveIndex(i);
      }
    }
  }

  deactivate(): void {
    this.#setActiveIndex(-1);
  }

  async create(
    path: string,
    data: ClanData,
    {
      active = true,
    }: {
      active?: boolean;
    } = {},
  ) {
    const meta = await api.clan.createClan(path, data);
    const clan = new Clan(meta, this);
    this.#setClans(this.#clans.length, clan);
    ClanList.#setIds(this.#clans.map(({ id }) => id));
    if (active) {
      this.#setActiveIndex(this.#clans.length - 1);
    }
  }

  async add({ id, active = true }: { id: string; active?: boolean }) {
    for (const [i, clan] of this.#clans.entries()) {
      if (clan.id === id) {
        return this.#setActiveIndex(i);
      }
    }

    const clan = await Clan.get(id, this);
    this.#setClans(this.#clans.length, clan);
    ClanList.#setIds(this.#clans.map(({ id }) => id));
    if (active) {
      this.#setActiveIndex(this.#clans.length - 1);
    }
  }
}

export class Clan {
  static async get(id: string, clans: ClanList) {
    const data = await api.clan.getClan(id);
    return new Clan(data, clans);
  }

  #clans: ClanList;
  readonly id: string;
  name: string;
  description: string | undefined;
  schema: ClanMeta["schema"];
  readonly machines: AccessorWithLatest<MachineList | undefined>;

  constructor(meta: ClanMeta, clans: ClanList) {
    this.#clans = clans;
    this.id = meta.id;
    this.name = meta.data.name;
    this.description = meta.data.description;
    this.schema = meta.schema;
    this.machines = createAsync(async () => await MachineList.get(this));
  }

  get isActive(): boolean {
    return this.#clans.active === this;
  }

  activate(): void {
    this.#clans.activate(this.id);
  }

  deactivate(): void {
    if (this.isActive) {
      this.#clans.deactivate();
    }
  }
}
