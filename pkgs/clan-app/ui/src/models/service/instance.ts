import { JSONSchema } from "json-schema-typed/draft-2020-12";
import { Accessor } from "solid-js";
import {
  Clan,
  ClanMethods,
  Clans,
  ClansMethods,
  Service,
  ServiceInstances,
  ServiceInstancesMethods,
} from "..";
import { SetStoreFunction } from "solid-js/store";

export type ServiceInstanceEntity = {
  data: ServiceInstanceData;
  readonly roles: ServiceInstanceRole[];
};
export type ServiceInstanceData = {
  name: string;
};

export type ServiceInstance = ServiceInstanceEntity & {
  readonly clan: Clan;
  readonly service: Service;
  readonly isActive: boolean;
  readonly index: number;
};

export function createServiceInstanceStore(
  instance: Accessor<ServiceInstance>,
  instancesValue: readonly [
    Accessor<ServiceInstances>,
    ServiceInstancesMethods,
  ],
  clanValue: readonly [Accessor<Clan>, ClanMethods],
  clansValue: readonly [Clans, ClansMethods],
): [Accessor<ServiceInstance>, ServiceInstanceMethods] {
  return [
    instance,
    instanceMethods(instance, instancesValue, clanValue, clansValue),
  ];
}

export type ServiceInstanceMethods = {
  setServiceInstance: SetStoreFunction<ServiceInstance>;
  activateServiceInstance(): void;
};
function instanceMethods(
  instance: Accessor<ServiceInstance>,
  [instances, { setServiceInstances, activateServiceInstance }]: readonly [
    Accessor<ServiceInstances>,
    ServiceInstancesMethods,
  ],
  [clan]: readonly [Accessor<Clan>, ClanMethods],
  [clans]: readonly [Clans, ClansMethods],
): ServiceInstanceMethods {
  // @ts-expect-error ...args won't infer properly for overloaded functions
  const setServiceInstance: SetStoreFunction<ServiceInstance> = (...args) => {
    // @ts-expect-error ...args won't infer properly for overloaded functions
    setServiceInstances("all", instance().index, ...args);
  };
  const self: ServiceInstanceMethods = {
    setServiceInstance,
    activateServiceInstance() {
      activateServiceInstance(instance());
    },
  };
  return self;
}

export type ServiceInstanceRole = {
  readonly id: string;
  settings: Record<string, unknown>;
  readonly settingsSchema: JSONSchema;
  machines: string[];
  tags: string[];
};

export function toServiceInstance(
  instance: ServiceInstanceEntity,
  serviceId: string,
  clanId: string,
  [clans, { existingClan }]: readonly [Clans, ClansMethods],
): ServiceInstance {
  return {
    ...instance,
    get clan(): Clan {
      return existingClan(clanId);
    },
    get service(): Service {
      const { clan } = this;
      const service = clan.services.find((service) => service.id === serviceId);
      if (!service) {
        throw new Error(`Service does not exist ${serviceId}`);
      }
      return service;
    },
    get isActive(): boolean {
      const { clan } = this;
      const i = clan.serviceInstances.activeIndex;
      if (i === undefined || i === -1) {
        return false;
      }
      return this.data.name === clan.serviceInstances.all[i].data.name;
    },
    get index(): number {
      const { clan } = this;
      return clan.serviceInstances.all.findIndex(
        (instance) => this.data.name === instance.data.name,
      );
    },
  };
}
