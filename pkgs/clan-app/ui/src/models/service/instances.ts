import { Accessor } from "solid-js";
import {
  Clan,
  ClanMethods,
  Clans,
  ClansMethods,
  Service,
  ServiceInstance,
} from "..";
import { produce, SetStoreFunction } from "solid-js/store";
import api from "../api";
import { toServiceInstance } from "./instance";

export type ServiceInstances = {
  all: ServiceInstance[];
  activeIndex: number;
  readonly activeServiceInstance: ServiceInstance | undefined;
};

export type ServiceInstancesMethods = {
  setServiceInstances: SetStoreFunction<ServiceInstances>;
  activateServiceInstance(
    item: number | ServiceInstance,
  ): ServiceInstance | undefined;
  createServiceInstance(service: Service): ServiceInstance;
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
    createServiceInstance(service: Service): ServiceInstance {
      return toServiceInstance(
        {
          data: {
            name: service.id,
            roles: Object.fromEntries(
              Object.entries(service.roles).map(([roleId]) => [
                roleId,
                {
                  id: roleId,
                  settings: {},
                  machines: [] as string[],
                  tags: [] as string[],
                },
              ]),
            ),
          },
        },
        () => service,
      );
    },
    async addServiceInstance(instance: ServiceInstance): Promise<void> {
      await api.clan.createServiceInstance(instance);
      setServiceInstances(
        "all",
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
