import { Accessor } from "solid-js";
import { produce, SetStoreFunction } from "solid-js/store";
import api from "../api";
import {
  Clan,
  ClanMethods,
  Clans,
  ClansMethods,
  Service,
  ServiceInstance,
  ServiceInstanceDataEntity,
  createServiceInstance,
  useClanContext,
  useClansContext,
} from "..";
import { ServiceEntity } from "./service";

export type ServiceInstances = {
  // clans, machines and services all use a Record<string, ...> type, instances
  // doesn't follow suit because an instance doesn't have a stable id, using a
  // record requires the key to be updated as well when the id (instance name)
  // is updated
  all: ServiceInstance[];
  readonly sorted: ServiceInstance[];
  activeServiceInstance: ServiceInstance | null;
};

export function createServiceInstancesStore(
  instances: Accessor<ServiceInstances>,
): [Accessor<ServiceInstances>, ServiceInstancesMethods] {
  const [clan, clanMethods] = useClanContext();
  const { setClan } = clanMethods;
  // @ts-expect-error ...args won't infer properly for overloaded functions
  const setInstances: SetStoreFunction<ServiceInstances> = (...args) => {
    // @ts-expect-error ...args won't infer properly for overloaded functions
    setClan("serviceInstances", ...args);
  };
  return [
    instances,
    instancesMethods(
      [instances, setInstances],
      [clan, clanMethods],
      useClansContext(),
    ),
  ];
}

export type ServiceInstancesMethods = {
  setServiceInstances: SetStoreFunction<ServiceInstances>;
  activateServiceInstance(
    item: string | ServiceInstance,
  ): ServiceInstance | null;
  addServiceInstance(
    data: ServiceInstanceDataEntity,
    service: Service,
  ): Promise<ServiceInstance>;
  updateServiceInstanceData(data: ServiceInstanceDataEntity): Promise<void>;
};
function instancesMethods(
  [instances, setInstances]: [
    Accessor<ServiceInstances>,
    SetStoreFunction<ServiceInstances>,
  ],
  [clan, { setClan }]: readonly [Accessor<Clan>, ClanMethods],
  [clans]: readonly [Clans, ClansMethods],
): ServiceInstancesMethods {
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
    setServiceInstances: setInstances,
    activateServiceInstance(item) {
      const instance = getInstance(item);
      if (clan().serviceInstances.activeServiceInstance === instance) {
        return null;
      }
      setInstances("activeServiceInstance", instance);
      return instance;
    },
    async addServiceInstance(
      data: ServiceInstanceDataEntity,
      service: Service,
    ): Promise<ServiceInstance> {
      await api.clan.createServiceInstance(data, service.id, clan().id);
      const instance = createServiceInstance({
        entity: { data },
        service: () => service,
        clan: () => service.clan,
      });
      setClan(
        "serviceInstances",
        produce((serviceInstances) => {
          serviceInstances.all.push(instance);
        }),
      );
      return instance;
    },
    async updateServiceInstanceData(data) {
      await api.clan.updateServiceInstanceData(data, clan().id);
    },
  };
  return self;
}

export function createServiceInstances(
  entities: Record<string, ServiceEntity>,
  clan: Accessor<Clan>,
): ServiceInstances {
  return {
    all: Object.entries(entities).flatMap(([serviceId, serviceEntity]) => {
      const service = () => {
        const service = clan().services.all[serviceId];
        if (!service) {
          throw new Error(`Service does not exist: ${serviceId}`);
        }
        return service;
      };
      return serviceEntity.instances.map((instanceEntity) =>
        createServiceInstance({
          entity: instanceEntity,
          service,
          clan,
        }),
      );
    }),
    get sorted() {
      return this.all
        .slice(0)
        .sort((a, b) => a.data.name.localeCompare(b.data.name));
    },
    activeServiceInstance: null,
  };
}
