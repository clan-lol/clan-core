import { Accessor } from "solid-js";
import api from "../api";
import {
  Clans,
  ClansMethods,
  DataSchema,
  Machines,
  ServiceInstances,
  Services,
} from "..";
import { reconcile, SetStoreFunction } from "solid-js/store";
import { MachineEntity } from "../machine/machine";
import { toMachines } from "../machine/machines";
import { toServices } from "../service/services";
import { ServiceEntity } from "../service/service";
import { toServiceInstances } from "../service/instances";

export type ClanEntity = {
  readonly id: string;
  readonly data: ClanEntityData;
  readonly dataSchema: DataSchema;
  readonly machines: Record<string, MachineEntity>;
  readonly services: Record<string, ServiceEntity>;
  readonly globalTags: Tags;
};

export type ClanEntityData = ClanMetaEntityData & {
  domain?: string;
};

export type Clan = Omit<ClanEntity, "data" | "machines" | "services"> & {
  data: ClanData;
  readonly machines: Machines;
  readonly services: Services;
  readonly clans: Clans;
  readonly members: ClanMember[];
  readonly index: number;
  readonly serviceInstances: ServiceInstances;
  readonly isActive: boolean;
};

export type ClanData = ClanEntityData;

export type ClanMetaEntity = {
  readonly id: string;
  readonly data: ClanMetaEntityData;
};
export type ClanMetaEntityData = {
  name: string;
  description?: string;
};
export type ClanMeta = Omit<ClanMetaEntity, "data"> & {
  readonly data: ClanMetaData;
  readonly clans: Clans;
  readonly index: number;
};

export type ClanMetaData = ClanMetaEntityData;

export type ClanMember = {
  type: "tag" | "machine";
  name: string;
};

export type Tags = {
  // TODO: rename backend's data.options to data.regular, options is too
  // overloaded a name
  readonly regular: string[];
  readonly special: string[];
};

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

export function toClan(entity: ClanEntity, clans: Clans): Clan {
  const { id } = entity;
  const clan: Accessor<Clan> = () => {
    const clan = clans.all.find((clan) => clan.id === id);
    if (!clan) {
      throw new Error(`Clan does not exist: ${id}`);
    }
    if (isClan(clan)) return clan;
    throw new Error(`Accessing a clan that has not been activated yet: ${id}`);
  };
  return {
    ...entity,
    get clans() {
      return clans;
    },
    machines: toMachines(entity.machines, clan),
    services: toServices(entity.services, clan),
    serviceInstances: toServiceInstances(clan),
    get members() {
      return [
        ...Object.keys(this.machines).map((name) => ({
          type: "machine" as const,
          name,
        })),
        ...this.globalTags.regular
          .concat(this.globalTags.special)
          .map((name) => ({ type: "tag" as const, name })),
      ].sort((a, b) => a.name.localeCompare(b.name));
    },
    get index() {
      return this.clans.all.findIndex((clan) => clan.id === this.id);
    },
    get isActive() {
      return clans.activeClan?.id === this.id;
    },
  };
}
export function toClanMeta(entity: ClanMetaEntity, clans: Clans): ClanMeta {
  return {
    ...entity,
    get clans() {
      return clans;
    },
    get index(): number {
      return this.clans.all.findIndex((clan) => clan.id === this.id);
    },
  };
}

export function isClan(clan: Clan | ClanMeta): clan is Clan {
  return "machines" in clan;
}
