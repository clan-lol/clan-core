import * as api from "@/src/api";
import { AccessorWithLatest, createAsync } from "@solidjs/router";
import { MachineList } from "./Machine";
import { ClanData, ClanMeta, DataSchema, Tags } from "@/src/api/clan";
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
  #setClans: (clans: Clan[]) => void;
  #activeIndex: Accessor<number>;
  #setActiveIndex: Setter<number>;

  private constructor(clans: Clan[]) {
    const [clansStore, setClansStore] = createStore(clans);
    this.#clans = clansStore;

    this.#setClans = (clans: Clan[]) => {
      setClansStore(clans);
      ClanList.#setIds(this.#clans.map(({ id }) => id));
    };
    const [activeIndex, setActiveIndex] = makePersisted(createSignal(-1), {
      name: "activeClanIndex",
    });
    this.#activeIndex = activeIndex;
    this.#setActiveIndex = (...args) => {
      if (this.active) {
        if (this.active.hasMachines()) {
          this.active.machines()?.deactivate();
        }
      }
      setActiveIndex(...args);
    };
  }
  get length() {
    return this.#clans.length;
  }
  [Symbol.iterator]() {
    return this.#clans[Symbol.iterator]();
  }
  entries(): ArrayIterator<[number, Clan]> {
    return this.#clans.entries();
  }

  get active(): Clan | null {
    const i = this.#activeIndex();
    return i === -1 ? null : this.#clans[i] || null;
  }

  activate(id: string): void {
    for (const [i, clan] of this.#clans.entries()) {
      if (clan.id === id) {
        this.#setActiveIndex(i);
      }
    }
  }

  deactivate(): void {
    this.#setActiveIndex(-1);
  }

  remove(id: string): void {
    for (const [i, clan] of this.#clans.entries()) {
      if (clan.id === id) {
        this.#setClans([
          ...this.#clans.slice(0, i),
          ...this.#clans.slice(i + 1),
        ]);
      }
    }
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
    this.#setClans([...this.#clans, clan]);
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
    this.#setClans([...this.#clans, clan]);
    if (active) {
      this.#setActiveIndex(this.#clans.length - 1);
    }
  }
}

export class Clan {
  static async get(id: string, clans: ClanList) {
    const meta = await api.clan.getClan(id);
    return new Clan(meta, clans);
  }

  readonly #clans: ClanList;
  readonly id: string;
  readonly data: ClanData;
  readonly #setData: SetStoreFunction<ClanData>;
  readonly schema: DataSchema;
  readonly hasMachines: Accessor<boolean>;
  readonly machines: AccessorWithLatest<MachineList | undefined>;
  readonly tags: AccessorWithLatest<Tags | undefined>;

  constructor(meta: ClanMeta, clans: ClanList) {
    this.#clans = clans;
    this.id = meta.id;
    [this.data, this.#setData] = createStore(meta.data);
    this.schema = meta.schema;
    const [hasMachines, setHasMachines] = createSignal(false);
    this.hasMachines = hasMachines;
    this.machines = createAsync(async () => {
      const machines = await MachineList.get(this);
      setHasMachines(true);
      return machines;
    });
    this.tags = createAsync(async () => await api.clan.getTags(this.id));
  }

  get isActive(): boolean {
    return this.#clans.active?.id === this.id;
  }

  activate(): void {
    this.#clans.activate(this.id);
  }

  deactivate(): void {
    if (this.isActive) {
      this.#clans.deactivate();
    }
  }

  async updateDate(data: ClanData): Promise<void> {
    await api.clan.updateClanData(this.id, data);
    this.#setData(data);
  }

  remove(): void {
    this.#clans.remove(this.id);
  }
}
