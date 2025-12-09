import { Accessor } from "solid-js";
import { Clan, ClanMethods, Clans, ClansMethods, ServiceInstance } from "..";
import { SetStoreFunction } from "solid-js/store";

export type ServiceInstances = {
  readonly all: ServiceInstance[];
  activeIndex: number;
  readonly activeServiceInstance: ServiceInstance | undefined;
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
