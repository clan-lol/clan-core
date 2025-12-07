import { Accessor, createEffect, createMemo, on } from "solid-js";
import {
  createStore,
  produce,
  reconcile,
  SetStoreFunction,
} from "solid-js/store";
import { captureStoreUpdates } from "@solid-primitives/deep";
import api from "./api";
import { MachineEntity, Machines, toMachines } from "./machine";
import { DataSchema } from ".";
import {
  Service,
  ServiceEntity,
  ServiceInstanceEntity,
  ServiceInstances,
} from "./service";

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

export function createClansStore(
  entity: Accessor<ClansEntity>,
): readonly [Clans, ClansMethods] {
  const [clans, setClans] = createStore<Clans>({
    all: [],
    activeIndex: entity().activeIndex,
    get activeClan(): Clan | undefined {
      return this.activeIndex === -1
        ? undefined
        : (this.all[this.activeIndex] as Clan);
    },
  });
  const clansValue = [clans, clansMethods([clans, setClans])] as const;

  createEffect(
    on(entity, (entity) => {
      setClans(
        produce((clans) => {
          clans.all = entity.all.map((clan) =>
            toClanOrClanMeta(clan, clansValue),
          );
          clans.activeIndex = entity.activeIndex;
        }),
      );
    }),
  );
  persistClans(clans);
  return clansValue;
}

function toClanOrClanMeta(
  entity: ClanEntity | ClanMetaEntity,
  [clans, { clanIndex }]: readonly [Clans, ClansMethods],
): Clan | ClanMeta {
  if (isNotMeta(entity)) {
    const self: Clan = {
      ...entity,
      machines: toMachines(entity.machines, clans),
      get index(): number {
        return clanIndex(this.id);
      },
      get isActive(): boolean {
        return clans.activeClan?.id === this.id;
      },
    };
    return self;
  }
  return {
    ...entity,
    get index(): number {
      return clanIndex(this.id);
    },
  } satisfies ClanMeta;
}

export type ClansMethods = {
  setClans: SetStoreFunction<Clans>;
  pickClanDir(): Promise<string>;
  clanIndex(item: string | Clan | ClanMeta): number;
  activateClan(item: number | Clan | ClanMeta): Promise<Clan | undefined>;
  deactivateClan(clan?: Clan): void;
  addExistingClan(id: string): Promise<Clan | undefined>;
  addNewClan(entity: NewClanEntity): Promise<Clan | undefined>;
  removeClan(item: number | Clan | ClanMeta): Clan | ClanMeta | undefined;
};
function clansMethods([clans, setClans]: [
  Clans,
  SetStoreFunction<Clans>,
]): ClansMethods {
  const self: ClansMethods = {
    setClans,
    async pickClanDir() {
      return api.clan.pickClanDir();
    },
    clanIndex(item: string | Clan | ClanMeta): number {
      if (typeof item === "string") {
        for (const [i, clan] of clans.all.entries()) {
          if (clan.id === item) {
            return i;
          }
        }
        return -1;
      }
      return self.clanIndex(item.id);
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
        const clan = toClanOrClanMeta(entity, [clans, self]) as Clan;
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
        return;
      }
    },

    async addNewClan(entity: NewClanEntity) {
      const created = await api.clan.createClan(entity);
      const clan = toClanOrClanMeta(created, [clans, self]) as Clan;
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
      const clan = toClanOrClanMeta(entity, [clans, self]) as Clan;
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
  clansValue: readonly [Clans, ClansMethods],
): readonly [Accessor<Clan>, ClanMethods] {
  return [clan, clanMethods(clan, clansValue)];
}

export type ClanMethods = {
  setClan: SetStoreFunction<Clan>;
  activateClan(): Promise<void>;
  deactivateClan(): void;
  updateClanData(data: Partial<ClanData>): Promise<void>;
  removeClan(): void;
};
function clanMethods(
  clan: Accessor<Clan>,
  [clans, { setClans, activateClan, deactivateClan, removeClan }]: readonly [
    Clans,
    ClansMethods,
  ],
): ClanMethods {
  // @ts-expect-error ...args won't infer properly for overloaded functions
  const setClan: SetStoreFunction<Clan> = (...args) => {
    // @ts-expect-error ...args won't infer properly for overloaded functions
    setClans("all", clan().index, ...args);
  };
  const self: ClanMethods = {
    setClan,
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
export type Clans = Omit<ClansEntity, "all"> & {
  all: (Clan | ClanMeta)[];
  readonly activeClan: Clan | undefined;
};

export type ClanEntity = {
  readonly id: string;
  readonly data: ClanData;
  readonly dataSchema: DataSchema;
  readonly machines: MachineEntity[];
  readonly services: ServiceEntity[];
  readonly serviceInstances: ServiceInstanceEntity[];
  readonly globalTags: Tags;
};
export type Clan = Omit<
  ClanEntity,
  "data" | "machines" | "services" | "serviceInstances"
> & {
  data: ClanData;
  readonly index: number;
  readonly machines: Machines;
  readonly services: Service[];
  readonly serviceInstances: ServiceInstances;
  readonly isActive: boolean;
};
export type NewClanEntity = Pick<ClanEntity, "id" | "data">;

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

export interface Tags {
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

function persistClans(clans: Clans) {
  const delta = createMemo(captureStoreUpdates(clans));
  createEffect(
    on(
      delta,
      (delta) => {
        for (const { path, value } of delta) {
          let clansChanged = false;
          let activeClanIndexChanged = false;
          let machinesChanged = false;
          let machinePositionsChanged = false;
          if (path.length === 0) {
            if ("all" in value) {
              clansChanged = true;
            }
            if ("activeIndex" in value) {
              activeClanIndexChanged = true;
            }
          } else {
            if (isPath(path, ["all"])) {
              clansChanged = true;
            } else if (isPath(path, ["activeIndex"])) {
              activeClanIndexChanged = true;
            } else if (
              isPath(path, ["all", "*", "machines", "all"]) ||
              (isPath(path, ["all", "*", "machines"]) && "all" in value)
            ) {
              machinesChanged = true;
            } else if (
              isAnyPath(path, [
                ["all", "*", "machines", "all", "*", "position"],
              ])
            ) {
              machinePositionsChanged = true;
            }
          }

          if (clansChanged) {
            machinesChanged = true;
            localStorage.setItem(
              "clanIds",
              JSON.stringify(clans.all.map(({ id }) => id)),
            );
          }
          if (activeClanIndexChanged) {
            localStorage.setItem("activeClanIndex", String(clans.activeIndex));
          }
          if (machinesChanged) {
            machinePositionsChanged = true;
          }
          if (machinePositionsChanged) {
            localStorage.setItem(
              "machinePositions",
              JSON.stringify(
                Object.fromEntries(
                  clans.all.map((clan) => {
                    if (isNotMeta(clan)) {
                      return [
                        clan.id,
                        Object.fromEntries(
                          clan.machines.all.map((machine) => [
                            machine.id,
                            machine.position,
                          ]),
                        ),
                      ];
                    }
                    return [];
                  }),
                ),
              ),
            );
          }
        }
      },
      { defer: true },
    ),
  );
}

function isPath(
  path: (string | number)[],
  targetPath: (string | number)[],
): boolean {
  if (path.length !== targetPath.length) return false;
  for (const [i, part] of path.entries()) {
    if (targetPath[i] !== "*" && targetPath[i] !== part) {
      return false;
    }
  }
  return true;
}

function isAnyPath(
  path: (string | number)[],
  targetPaths: (string | number)[][],
): boolean {
  for (const targetPath of targetPaths) {
    if (isPath(path, targetPath)) return true;
  }
  return false;
}
