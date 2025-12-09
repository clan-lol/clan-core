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
export type Clan = Omit<ClanEntity, "data" | "machines" | "services"> & {
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

export function toClanOrClanMeta(
  entity: ClanEntity | ClanMetaEntity,
  clansValue: readonly [Clans, ClansMethods],
): Clan | ClanMeta {
  const [clans, { clanIndex, existingClan }] = clansValue;
  if (isClan(entity)) {
    const self: Clan = {
      ...entity,
      machines: toMachines(entity.machines, entity.id, clansValue),
      services: entity.services.map((service) =>
        toService(service, entity.id, clansValue),
      ),
      serviceInstances: {
        get all() {
          const clan = existingClan(entity.id);
          return clan.services.flatMap((service) => service.instances);
        },
        activeIndex: -1,
        get activeServiceInstance(): ServiceInstance | undefined {
          return this.activeIndex == -1
            ? undefined
            : this.all[this.activeIndex];
        },
      },
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

export function isClan(clan: Clan | ClanMeta): clan is Clan;
export function isClan(clan: ClanEntity | ClanMetaEntity): clan is ClanEntity;
export function isClan(
  clan: Clan | ClanEntity | ClanMeta | ClanMetaEntity,
): clan is Clan | ClanEntity {
  return "machines" in clan;
}
