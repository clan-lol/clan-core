import { JSONSchema } from "json-schema-typed/draft-2020-12";
import api from "./api";
import { Clan, Clans, ClanMethods, ClansMethods } from "./clan";
import { createStore, SetStoreFunction } from "solid-js/store";
import { createAsync } from "@solidjs/router";
import { Accessor } from "solid-js";
import { Machine, Machines, MachineMethods, MachinesMethods } from "./machine";

export type ServiceEntity = {
  readonly id: string;
  readonly instances: ServiceInstanceEntity[];
};
export type Service = Omit<ServiceEntity, "instances"> & {
  readonly clan: Clan;
  readonly instances: ServiceInstance[];
};

export type ServiceInstances = {
  readonly all: ServiceInstance[];
  activeIndex: number;
  readonly activeServiceInstance: ServiceInstance | undefined;
};

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

export function createServiceInstancesStore(
  instances: Accessor<ServiceInstances>,
  clanValue: readonly [Accessor<Clan>, ClanMethods],
  clansValue: readonly [Clans, ClansMethods],
): [Accessor<ServiceInstances>, ServiceInstancesMethods] {
  return [instances, instancesMethods(instances, clanValue, clansValue)];
}

export type ServiceInstancesMethods = {
  setServiceInstances: SetStoreFunction<ServiceInstances>;
  activateServiceInstance(
    item: number | ServiceInstance,
  ): ServiceInstance | undefined;
};
function instancesMethods(
  instances: Accessor<ServiceInstances>,
  [clan, { setClan }]: readonly [Accessor<Clan>, ClanMethods],
  [clans]: readonly [Clans, ClansMethods],
): ServiceInstancesMethods {
  // @ts-expect-error ...args won't infer properly for overloaded functions
  const setServiceInstances: SetStoreFunction<ServiceInstances> = (...args) => {
    // @ts-expect-error ...args won't infer properly for overloaded functions
    setClan("serviceInstances", ...args);
  };

  const self: ServiceInstancesMethods = {
    setServiceInstances,
    activateServiceInstance(item) {
      if (typeof item === "number") {
        const i = item;
        if (i < 0 || i >= instances().all.length) {
          throw new Error(
            `activateServiceInstance called with invalid index: ${i}`,
          );
        }
        if (instances().activeIndex === i) return;

        const instance = instances().all[i];
        setServiceInstances("activeIndex", i);
        return instance;
      }
      return self.activateServiceInstance(item.index);
    },
  };
  return self;
}

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

export function toService(
  entity: ServiceEntity,
  clanId: string,
  clansValue: readonly [Clans, ClansMethods],
): Service {
  const [, { existingClan }] = clansValue;
  return {
    ...entity,
    get clan(): Clan {
      return existingClan(clanId);
    },
    instances: entity.instances.map((instance) =>
      toServiceInstance(instance, entity.id, clanId, clansValue),
    ),
  };
}
function toServiceInstance(
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
