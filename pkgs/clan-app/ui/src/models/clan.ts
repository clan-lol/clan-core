import { Accessor, createEffect, createMemo, on } from "solid-js";
import {
  createStore,
  produce,
  reconcile,
  SetStoreFunction,
} from "solid-js/store";
import { captureStoreUpdates } from "@solid-primitives/deep";
import api from "./api";
import { Machine, MachineData, MachineEntity, MachineList } from "./Machine";
import { DataSchema } from ".";

export async function initClans(): Promise<ClansEntity> {
  const ids: string[] = (() => {
    const s = localStorage.getItem("clanIds");
    if (s === null) {
      return [];
    }
    return JSON.parse(s);
  })();
  const activeIndex: number = (() => {
    const s = localStorage.getItem("activeClanIndex");
    if (s === null) {
      return -1;
    }
    return parseInt(s, 10);
  })();

  return await api.clan.getClans(ids, activeIndex);
}

function fromEntity(
  entity: ClanEntity | ClanMetaEntity,
  clans: Clans,
): Clan | ClanMeta {
  function getIndex(id: string): number {
    for (const [i, clan] of clans.all.entries()) {
      if (clan.id === id) {
        return i;
      }
    }
    return -1;
  }

  if (isNotMeta(entity)) {
    return {
      ...entity,
      get index(): number {
        return getIndex(this.id);
      },
      get isActive(): boolean {
        return clans.activeClan?.id === this.id;
      },
    };
  }
  return {
    ...entity,
    get index(): number {
      return getIndex(this.id);
    },
  };
}

export function createClansStore(
  entity: Accessor<ClansEntity>,
): [Clans, ClansSetters] {
  const [clans, setClans] = createStore<Clans>({
    all: [],
    activeIndex: entity().activeIndex,
    get activeClan(): Clan | undefined {
      return this.activeIndex === -1
        ? undefined
        : (this.all[this.activeIndex] as Clan);
    },
  });
  createEffect(
    on(entity, (entity) => {
      setClans(
        produce((clans) => {
          clans.all = entity.all.map((clan) => fromEntity(clan, clans));
          clans.activeIndex = entity.activeIndex;
        }),
      );
    }),
  );
  const delta = createMemo(captureStoreUpdates(clans));
  createEffect(
    on(
      delta,
      (delta) => {
        for (const { path, value } of delta) {
          let arrayChanged = false;
          let indexChanged = false;
          switch (path.length) {
            case 0:
              if ("all" in value) {
                arrayChanged = true;
              }
              if ("activeIndex" in value) {
                indexChanged = true;
              }
              break;
            case 1:
              if (path[0] === "all") {
                arrayChanged = true;
              }
              if (path[0] === "activeIndex") {
                indexChanged = true;
              }
              break;
          }
          if (arrayChanged) {
            localStorage.setItem(
              "clanIds",
              JSON.stringify(clans.all.map(({ id }) => id)),
            );
          }
          if (indexChanged) {
            localStorage.setItem("activeClanIndex", String(clans.activeIndex));
          }
        }
      },
      { defer: true },
    ),
  );
  return [clans, clansSetters([clans, setClans])];
}

export type ClansSetters = {
  setClans: SetStoreFunction<Clans>;
  pickClanDir(): Promise<string>;
  activateClan(item: number | Clan | ClanMeta): Promise<Clan | undefined>;
  deactivateClan(): void;
  addExistingClan(id: string): Promise<Clan | undefined>;
  addNewClan(data: ClanNewEntity): Promise<Clan | undefined>;
  removeClan(item: number | Clan | ClanMeta): Clan | ClanMeta | undefined;
};
function clansSetters([clans, setClans]: [
  Clans,
  SetStoreFunction<Clans>,
]): ClansSetters {
  const self: ClansSetters = {
    setClans,
    async pickClanDir() {
      return api.clan.pickClanDir();
    },
    async activateClan(item) {
      if (typeof item === "number") {
        const i = item;
        const c = clans.all[i];
        if (!c) return;

        if (isNotMeta(c)) {
          setClans("activeIndex", i);
          return c;
        }
        const meta = c;
        const entity = await api.clan.getClan(meta.id);
        const clan = fromEntity(entity, clans) as Clan;
        setClans(
          produce((clans) => {
            clans.all[i] = clan;
            clans.activeIndex = i;
          }),
        );
        return clan;
      }

      return await self.activateClan(item.index);
    },
    deactivateClan(clan?: Clan) {
      if (!clan) {
        setClans("activeIndex", -1);
        return;
      }
      if (clan.index === clans.activeIndex) {
        setClans("activeIndex", -1);
      }
    },

    async addNewClan(data: ClanNewEntity) {
      const entity = await api.clan.createClan(data);
      const clan = fromEntity(entity, clans) as Clan;
      setClans(
        produce((clans) => {
          clans.activeIndex = clans.all.length;
          clans.all.push(clan);
        }),
      );
      return clans.all.at(-1) as Clan;
    },

    async addExistingClan(id: string) {
      for (const [i, clan] of clans.all.entries()) {
        if (clan.id === id) {
          return self.activateClan(i);
        }
      }
      const entity = await api.clan.getClan(id);
      const clan = fromEntity(entity, clans) as Clan;
      setClans(
        produce((clans) => {
          clans.activeIndex = clans.all.length;
          clans.all.push(clan);
        }),
      );
      return clans.all.at(-1) as Clan;
    },
    removeClan(item) {
      if (typeof item === "number") {
        const i = item;
        const clan = clans.all[i];
        if (!clan) return;
        setClans(
          produce((clans) => {
            clans.all.splice(i, 1);
            if (clans.activeIndex === i) {
              clans.activeIndex = -1;
            }
          }),
        );
        return clan;
      }
      return self.removeClan(item.index);
    },
  };
  return self;
}

export function createClanStore(
  clan: Accessor<Clan>,
  [clans, clansSetters]: [Clans, ClansSetters],
): [Accessor<Clan>, ClanSetters] {
  return [clan, clanSetters(clan, [clans, clansSetters])];
}

export type ClanSetters = {
  activateClan(): Promise<void>;
  deactivateClan(): void;
  updateClanData(data: Partial<ClanData>): Promise<void>;
  removeClan(): void;
};
function clanSetters(
  clan: Accessor<Clan>,
  [clans, { setClans, activateClan, deactivateClan, removeClan }]: [
    Clans,
    ClansSetters,
  ],
): ClanSetters {
  // @ts-expect-error ...args won't infer properly for overloaded functions
  const setClan: SetStoreFunction<Clan> = (...args) => {
    // @ts-expect-error ...args won't infer properly for overloaded functions
    setClans("all", clan().index, ...args);
  };
  const self: ClanSetters = {
    async activateClan() {
      await activateClan(clan());
    },
    deactivateClan() {
      if (clan().isActive) {
        deactivateClan();
      }
    },

    async updateClanData(data) {
      // TODO: Use partial update once supported by backend and solidjs
      // https://github.com/solidjs/solid/issues/2475
      const d = { ...clan().data, ...data };
      await api.clan.updateClanData(clan().id, d);
      setClan("data", reconcile(d));
    },
    removeClan() {
      removeClan(clan());
    },
  };
  return self;
}

export type ClansEntity = {
  readonly all: (ClanEntity | ClanMetaEntity)[];
  activeIndex: number;
};
export type Clans = ClansEntity & {
  all: (Clan | ClanMeta)[];
  readonly activeClan: Clan | undefined;
};

export type ClanEntity = {
  readonly id: string;
  readonly data: ClanData;
  readonly dataSchema: DataSchema;
  readonly machines: MachineEntity[];
  // readonly services: ServiceEntity[];
  readonly globalTags: GlobalTags;
};
export type Clan = ClanEntity & {
  data: ClanData;
  readonly index: number;
  readonly machines: MachineList;
  // readonly services: ServiceList;
  readonly isActive: boolean;
};
export type ClanNewEntity = Pick<ClanEntity, "id" | "data">;

export type ClanMetaEntity = {
  readonly id: string;
  readonly data: ClanMetaData;
};
export type ClanMeta = ClanMetaEntity & {
  readonly index: number;
};

export type ClanMetaData = {
  name: string;
  description?: string;
};

export type ClanData = ClanMetaData & {
  domain?: string;
  // dataSchema: JSONSchema;
  // machines: MachineData[];
  // services: ServiceData[];
  // globalTags: globalTags;
};

export interface GlobalTags {
  // TODO: rename backend's data.options to data.regular, options is too
  // overloaded a name
  readonly regular: string[];
  readonly special: string[];
}

function isNotMeta(clan: Clan | ClanMeta): clan is Clan;
function isNotMeta(clan: ClanEntity | ClanMetaEntity): clan is ClanEntity;
function isNotMeta(
  clan: Clan | ClanEntity | ClanMeta | ClanMetaEntity,
): clan is Clan | ClanEntity {
  return "machines" in clan;
}
