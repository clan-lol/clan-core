import { Accessor, createEffect, createMemo, on } from "solid-js";
import { createStore, produce, SetStoreFunction } from "solid-js/store";
import { captureStoreUpdates, NestedUpdate } from "@solid-primitives/deep";
import api from "../api";
import { Clan, ClanMeta, ClanDataEntity } from "..";
import {
  ClanEntity,
  ClanMetaEntity,
  isClan,
  createClan,
  createClanMeta,
} from "./clan";
import { mapObjectValues } from "@/src/util";

export type ClansEntity = {
  readonly all: (ClanEntity | ClanMetaEntity)[];
  readonly activeIndex: number;
};
export type Clans = {
  all: (Clan | ClanMeta)[];
  activeClan: Clan | null;
};

export async function initClans(): Promise<ClansEntity> {
  const ids: string[] = (() => {
    const s = localStorage.getItem("clanIds");
    if (s === null) {
      return [];
    }
    return JSON.parse(s);
  })();
  let activeIndex: number = (() => {
    const s = localStorage.getItem("activeClanIndex");
    if (s === null) {
      return -1;
    }
    return parseInt(s, 10);
  })();

  if (ids.length === 0) {
    return {
      all: [],
      activeIndex: -1,
    };
  }

  // This means localStorage has been corrupted, which shouldn't happen.
  // Just make the first clan to be the active one to be defensive
  if (activeIndex >= ids.length) {
    activeIndex = 0;
  }

  return {
    all: await api.clan.getClans(ids, activeIndex),
    activeIndex,
  };
}

export function createClansStore(
  entity: Accessor<ClansEntity>,
): readonly [Clans, ClansMethods] {
  const [clans, setClans] = createStore<Clans>({
    all: [],
    activeClan: null,
  });
  const methods = clansMethods([clans, setClans]);
  createEffect(
    on(entity, (entity) => {
      const all = entity.all.map((clanEntity, i) =>
        i === entity.activeIndex
          ? createClan(clanEntity as ClanEntity, clans)
          : createClanMeta(clanEntity as ClanMetaEntity, clans),
      );
      const activeClan =
        entity.activeIndex === -1 ? null : (all[entity.activeIndex] as Clan);
      setClans(
        produce((clans) => {
          clans.all = all;
          clans.activeClan = activeClan;
        }),
      );
    }),
  );
  persistClans(clans);

  return [clans, methods];
}

export type ClansMethods = {
  setClans: SetStoreFunction<Clans>;
  pickClanDir(): Promise<string>;
  activateClan(item: Clan | ClanMeta | string): Promise<Clan | null>;
  deactivateClan(): void;
  deactivateClan(item: Clan | string): Clan | null;
  loadClan(id: string, opts?: { active?: boolean }): Promise<Clan | null>;
  createClan(
    id: string,
    data: ClanDataEntity,
    opts?: { active?: boolean },
  ): Promise<Clan>;
  removeClan(item: Clan | ClanMeta | string): Clan | ClanMeta;
};
function clansMethods([clans, setClans]: [
  Clans,
  SetStoreFunction<Clans>,
]): ClansMethods {
  function getClan(item: Clan | string): readonly [Clan, number];
  function getClan(item: ClanMeta | string): readonly [ClanMeta, number];
  function getClan(
    item: Clan | ClanMeta | string,
  ): readonly [Clan | ClanMeta, number];
  function getClan(
    item: Clan | ClanMeta | string,
  ): readonly [Clan | ClanMeta, number] {
    if (typeof item === "string") {
      const id = item;
      for (const [i, clan] of clans.all.entries()) {
        if (clan.id === id) {
          return [clan, i];
        }
      }
      throw new Error(`Clan does not exist: ${id}`);
    }
    const clan = item;
    const i = clans.all.indexOf(item);
    if (i === -1) {
      throw new Error(
        `This clan does not belong to the known clans: ${clan.id}`,
      );
    }
    return [clan, i];
  }

  function deactivateClan(): void;
  function deactivateClan(item: Clan | string): Clan | null;
  function deactivateClan(item?: Clan | string): void | Clan | null {
    if (!item) {
      setClans(
        produce((clans) => {
          clans.activeClan = null;
        }),
      );
      return;
    }
    const [clan] = getClan(item);
    if (clan === clans.activeClan) {
      return null;
    }
    setClans(
      produce((clans) => {
        clans.activeClan = clan;
      }),
    );
    return clan;
  }

  const self: ClansMethods = {
    setClans,
    async pickClanDir() {
      return api.clan.pickClanDir();
    },
    async activateClan(item) {
      const [clan, i] = getClan(item);

      if (isClan(clan)) {
        if (clan === clans.activeClan) {
          return null;
        }
        setClans(
          produce((clans) => {
            clans.activeClan = clan;
          }),
        );
        return clan;
      }
      const entity = await api.clan.getClan(clan.id);
      const newClan = createClan(entity as ClanEntity, clans);
      setClans(
        produce((clans) => {
          clans.all[i] = newClan;
          clans.activeClan = newClan;
        }),
      );
      return newClan;
    },
    deactivateClan,
    async loadClan(id, { active = true } = {}) {
      const [clan] = getClan(id);
      if (clan) {
        if (active && clans.activeClan !== clan) {
          setClans(
            produce((clans) => {
              clans.activeClan = clan;
            }),
          );
        }
        return null;
      }
      const entity = await api.clan.getClan(id);
      const newClan = createClan(entity, clans);
      setClans(
        produce((clans) => {
          clans.all.push(newClan);
          if (active) {
            clans.activeClan = newClan;
          }
        }),
      );
      return newClan;
    },
    async createClan(id, data, { active = true } = {}) {
      await api.clan.createClan(id, data);
      const newClan = createClan(
        {
          id,
          data,
          dataSchema: {},
          machines: {},
          services: {},
          globalTags: {
            regular: [],
            special: ["all", "nixos", "darwin"],
          },
        },
        clans,
      );
      setClans(
        produce((clans) => {
          clans.all.push(newClan);
          if (active) {
            clans.activeClan = newClan;
          }
        }),
      );
      return newClan;
    },
    removeClan(item) {
      const [clan, i] = getClan(item);
      setClans(
        produce((clans) => {
          clans.all.splice(i, 1);
          if (clans.activeClan === clan) {
            clans.activeClan = null;
          }
        }),
      );
      return clan;
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
  let clansChanged = false;
  let activeClanChanged = false;
  let machinesChanged = false;
  let machinePositionsChanged = false;

  for (const change of changes) {
    if (isPath(change, ["all"])) {
      clansChanged = true;
    } else if (isPath(change, ["activeClan"])) {
      activeClanChanged = true;
    } else if (
      isAnyPath(change, [
        ["all", "*", "machines", "all"],
        ["all", "*", "machines", "all", "*"],
      ])
    ) {
      machinesChanged = true;
    } else if (
      isPath(change, ["all", "*", "machines", "all", "*", "data", "position"])
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
  if (activeClanChanged) {
    localStorage.setItem(
      "activeClanIndex",
      String(clans.activeClan ? clans.activeClan.index : -1),
    );
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
                mapObjectValues(
                  clan.machines.all,
                  ([, machine]) => machine.data.position,
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

function isPath(
  change: NestedUpdate<Clans>,
  targetPath: (string | number)[],
): boolean {
  // @ts-expect-error AllNestedObjects results in infinite recurrsion for
  // circular types
  const { path, value } = change;
  if (path.length === targetPath.length) {
    return pathMatches(path, targetPath);
  }
  const base = path.slice(0, targetPath.length - 1);
  const lastIndex = targetPath.length - 1;
  if (base.length === lastIndex) {
    const last = targetPath[lastIndex]!;
    return pathMatches(base, targetPath.slice(0, lastIndex)) && last in value;
  }
  return false;
}

function isAnyPath(
  change: NestedUpdate<Clans>,
  targetPaths: (string | number)[][],
): boolean {
  return targetPaths.some((targetPath) => isPath(change, targetPath));
}

function pathMatches(
  path: (string | number)[],
  targetPath: (string | number)[],
): boolean {
  if (path.length !== targetPath.length) {
    return false;
  }
  for (const [i, part] of path.entries()) {
    if (targetPath[i] !== "*" && path[i] !== part) {
      return false;
    }
  }
  return true;
}
