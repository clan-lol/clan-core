import { Accessor } from "solid-js";
import {
  Clan,
  ClanMethods,
  Clans,
  ClansMethods,
  Service,
  ServiceInstance,
  ServiceInstanceEntityData,
} from "..";
import { produce, SetStoreFunction } from "solid-js/store";
import api from "../api";
import { toServiceInstance } from "./instance";

export type ServiceInstances = {
  readonly sorted: ServiceInstance[];
  activeServiceInstance: ServiceInstance | null;
};

export type ServiceInstancesMethods = {
  setServiceInstances: SetStoreFunction<ServiceInstances>;
  activateServiceInstance(
    item: string | ServiceInstance,
  ): ServiceInstance | null;
  createServiceInstance(
    data: ServiceInstanceEntityData,
    service: Service,
  ): Promise<ServiceInstance>;
  addServiceInstance(instance: ServiceInstance): Promise<void>;
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
  function getInstance(item: string | ServiceInstance): ServiceInstance {
    if (typeof item === "string") {
      const name = item;
      for (const [, service] of Object.entries(clan().services.all)) {
        for (const [, instance] of service.instances.entries()) {
          if (instance.data.name === name) {
            return instance;
          }
        }
      }
      throw new Error(`Service instance does not exist: ${name}`);
    }
    const instance = item;
    for (const [, service] of Object.entries(clan().services.all)) {
      for (const [, inst] of service.instances.entries()) {
        if (inst === instance) {
          return instance;
        }
      }
    }
    throw new Error(
      `This service instance does not belong to the known service instances: ${instance.data.name}`,
    );
  }

  const self: ServiceInstancesMethods = {
    setServiceInstances,
    activateServiceInstance(item) {
      const instance = getInstance(item);
      if (clan().serviceInstances.activeServiceInstance === instance) {
        return null;
      }
      setServiceInstances("activeServiceInstance", instance);
      return instance;
    },
    async createServiceInstance(data, service) {
      await api.clan.createServiceInstance(data, service.id, service.clan.id);
      return toServiceInstance({ data }, () => service);
    },
    async addServiceInstance(instance: ServiceInstance): Promise<void> {
      await api.clan.createServiceInstance(
        instance.data,
        instance.service.id,
        instance.clan.id,
      );
      setClan(
        "services",
        "all",
        instance.service.id,
        "instances",
        produce((instances) => {
          instances.push(instance);
        }),
      );
    },
  };
  return self;
}

export function createServiceInstancesStore(
  instances: Accessor<ServiceInstances>,
  clanValue: readonly [Accessor<Clan>, ClanMethods],
  clansValue: readonly [Clans, ClansMethods],
): [Accessor<ServiceInstances>, ServiceInstancesMethods] {
  return [instances, instancesMethods(instances, clanValue, clansValue)];
}

export function toServiceInstances(clan: Accessor<Clan>) {
  return {
    get sorted() {
      return Object.values(clan().services.all)
        .flatMap((service) => service.instances)
        .sort((a, b) => a.data.name.localeCompare(b.data.name));
    },
    activeServiceInstance: null,
  };
}
