import { Accessor } from "solid-js";
import api from "../api";
import {
  Clans,
  ClansMethods,
  DataSchema,
  Machines,
  Service,
  ServiceInstance,
  ServiceInstances,
} from "..";
import { reconcile, SetStoreFunction } from "solid-js/store";
import { MachineEntity } from "../machine/machine";
import { toMachines } from "../machine/machines";
import { ServiceEntity, toService } from "../service/service";

export type ClanEntity = {
  readonly id: string;
  readonly data: ClanData;
  readonly dataSchema: DataSchema;
  readonly machines: MachineEntity[];
  readonly services: ServiceEntity[];
  readonly globalTags: Tags;
};
export type Clan = {
  readonly id: string;
  data: ClanData;
  readonly dataSchema: DataSchema;
  readonly machines: Machines;
  readonly services: Service[];
  readonly globalTags: Tags;
  readonly clans: Clans;
  readonly members: ClanMember[];
  readonly index: number;
  readonly serviceInstances: ServiceInstances;
  readonly isActive: boolean;
};
export type NewClanEntity = Pick<ClanEntity, "id" | "data">;

export type ClanMetaEntity = {
  readonly id: string;
  readonly data: ClanMetaData;
};
export type ClanMeta = {
  readonly id: string;
  readonly data: ClanMetaData;
  readonly clans: Clans;
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
export function toClanOrClanMeta(entity: ClanEntity, clans: Clans): Clan;
export function toClanOrClanMeta(
  entity: ClanMetaEntity,
  clans: Clans,
): ClanMeta;
export function toClanOrClanMeta(
  entity: ClanEntity | ClanMetaEntity,
  clans: Clans,
): Clan | ClanMeta {
  const { id } = entity;
  const clan: Accessor<Clan> = () => {
    const i = clans.all.findIndex((clan) => clan.id === id);
    if (i === -1) {
      throw new Error(`Clan does not exist: ${id}`);
    }
    const clan = clans.all[i];
    if (isClan(clan)) return clan;
    throw new Error(`Accessing a clan that has not been activated yet: ${id}`);
  };
  if (isClan(entity)) {
    const self: Clan = {
      ...entity,
      get clans() {
        return clans;
      },
      machines: toMachines(entity.machines, clan),
      services: entity.services.map((service) => toService(service, clan)),
      serviceInstances: {
        get all() {
          return clan().services.flatMap((service) => service.instances);
        },
        activeIndex: -1,
        get activeServiceInstance(): ServiceInstance | undefined {
          return this.activeIndex == -1
            ? undefined
            : this.all[this.activeIndex];
        },
      },
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
    return self;
  }
  const self: ClanMeta = {
    ...entity,
    get clans() {
      return clans;
    },
    get index(): number {
      return this.clans.all.findIndex((clan) => clan.id === this.id);
    },
  };
  return self;
}

export function isClan(clan: Clan | ClanMeta): clan is Clan;
export function isClan(clan: ClanEntity | ClanMetaEntity): clan is ClanEntity;
export function isClan(
  clan: Clan | ClanEntity | ClanMeta | ClanMetaEntity,
): clan is Clan | ClanEntity {
  return "machines" in clan;
}
