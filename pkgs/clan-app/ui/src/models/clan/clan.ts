import { Accessor } from "solid-js";
import api from "../api";
import {
  Clans,
  ClansMethods,
  DataSchema,
  Machines,
  ServiceInstances,
  Services,
  useClansContext,
} from "..";
import { SetStoreFunction } from "solid-js/store";
import { MachineEntity } from "../machine/machine";
import { createMachines } from "../machine/machines";
import { createServices } from "../service/services";
import { ServiceEntity } from "../service/service";
import { createServiceInstances } from "../service/instances";

export type ClanEntity = {
  readonly id: string;
  readonly data: ClanDataEntity;
  readonly dataSchema: DataSchema;
  readonly machines: Record<string, MachineEntity>;
  readonly services: Record<string, ServiceEntity>;
  readonly globalTags: Tags;
};

export type ClanDataEntity = ClanMetaDataEntity & {
  domain?: string;
};
export type ClanMemberEntity = {
  readonly type: "tag" | "machine";
  readonly name: string;
};

export type Clan = Omit<
  ClanEntity,
  "data" | "machines" | "services" | "serviceInstances"
> & {
  readonly clans: Clans;
  readonly machines: Machines;
  readonly services: Services;
  data: ClanData;
  readonly members: ClanMember[];
  readonly index: number;
  serviceInstances: ServiceInstances;
  readonly isActive: boolean;
};

export type ClanData = ClanDataEntity;

export type ClanMetaEntity = {
  readonly id: string;
  readonly data: ClanMetaDataEntity;
};
export type ClanMetaDataEntity = {
  name: string;
  description?: string;
};
export type ClanMeta = Omit<ClanMetaEntity, "data"> & {
  readonly data: ClanMetaData;
  readonly clans: Clans;
  readonly index: number;
};

export type ClanMetaData = ClanMetaDataEntity;

export type ClanMember = ClanMemberEntity;

export type Tags = {
  // TODO: rename backend's data.options to data.regular, options is too
  // overloaded a name
  readonly regular: string[];
  readonly special: string[];
};

export function createClanStore(
  clan: Accessor<Clan>,
): readonly [Accessor<Clan>, ClanMethods] {
  return [clan, createClanMethods(clan, useClansContext())];
}

export type ClanMethods = {
  setClan: SetStoreFunction<Clan>;
  activateClan(): Promise<void>;
  deactivateClan(): void;
  updateClanData(data: Partial<ClanData>): Promise<void>;
  removeClan(): void;
};
export function createClanMethods(
  clan: Accessor<Clan>,
  [clans, { setClans, activateClan, deactivateClan, removeClan }]: readonly [
    Clans,
    ClansMethods,
  ],
): ClanMethods {
  // @ts-expect-error ...args won't infer properly for overloaded functions
  const setClan: SetStoreFunction<Clan> = (...args) => {
    const i = clan().index;
    if (i === -1) {
      throw new Error(
        `This clan does not belong to the known clan: ${clan().id}`,
      );
    }
    // @ts-expect-error ...args won't infer properly for overloaded functions
    setClans("all", i, ...args);
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
      setClan("data", d);
    },
    removeClan() {
      removeClan(clan());
    },
  };
  return self;
}

export function createClan(entity: ClanEntity, clans: Clans): Clan {
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
    machines: createMachines(entity.machines, clan),
    services: createServices(entity.services, clan),
    serviceInstances: createServiceInstances(entity.services, clan),
    get members() {
      return [
        ...Object.keys(this.machines.all).map((name) => ({
          type: "machine" as const,
          name,
        })),
        ...this.globalTags.regular
          .concat(this.globalTags.special)
          .map((name) => ({ type: "tag" as const, name })),
      ].sort((a, b) => a.name.localeCompare(b.name));
    },
    get index() {
      return this.clans.all.indexOf(this);
    },
    get isActive() {
      return clans.activeClan === this;
    },
  };
}
export function createClanMeta(entity: ClanMetaEntity, clans: Clans): ClanMeta {
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
