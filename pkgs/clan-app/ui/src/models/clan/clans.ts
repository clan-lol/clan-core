import { Accessor, createEffect, createMemo, on } from "solid-js";
import { createStore, produce, SetStoreFunction } from "solid-js/store";
import { captureStoreUpdates, NestedUpdate } from "@solid-primitives/deep";
import api from "../api";
import { Clan, ClanMeta } from "..";
import {
  ClanEntity,
  ClanMetaEntity,
  isClan,
  toClanOrClanMeta,
  NewClanEntity,
} from "./clan";

export type ClansEntity = {
  readonly all: (ClanEntity | ClanMetaEntity)[];
  activeIndex: number;
};
export type Clans = Omit<ClansEntity, "all"> & {
  all: (Clan | ClanMeta)[];
  readonly activeClan: Clan | undefined;
};

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

export type ClansMethods = {
  setClans: SetStoreFunction<Clans>;
  pickClanDir(): Promise<string>;
  clanIndex(item: string | Clan | ClanMeta): number;
  existingClan(id: string): Clan;
  activateClan(
    item: number | string | Clan | ClanMeta,
  ): Promise<Clan | undefined>;
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
    existingClan(id: string): Clan {
      const i = self.clanIndex(id);
      if (i === -1) {
        throw new Error(`Clan does not exist: ${id}`);
      }
      const clan = clans.all[i];
      if (isClan(clan)) return clan;
      throw new Error(
        `Accessing a clan that has not been activated yet: ${id}`,
      );
    },
    async activateClan(item) {
      if (typeof item === "number") {
        const i = item;
        if (i < 0 || i >= clans.all.length) {
          throw new Error(`activateClan called with invalid index: ${i}`);
        }
        if (clans.activeIndex === i) return;

        const c = clans.all[i];
        if (isClan(c)) {
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
      let id: string;
      if (typeof item === "string") {
        id = item;
      } else {
        id = item.id;
      }
      const i = self.clanIndex(id);
      if (i === -1) {
        throw new Error(`Clan does not exist: ${id}`);
      }
      return await self.activateClan(i);
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

function persistClans(clans: Clans) {
  const changes = createMemo(captureStoreUpdates(clans));
  createEffect(
    on(changes, (changes) => persistClansChanges(changes, clans), {
      defer: true,
    }),
  );
}

function persistClansChanges(
  changes: NestedUpdate<Clans>[],
  clans: Clans,
): void {
  // @ts-expect-error it seems NestedUpdate can't handle circular data
  for (const { path, value } of changes) {
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
        isAnyPath(path, [["all", "*", "machines", "all", "*", "position"]])
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
              if (isClan(clan)) {
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
