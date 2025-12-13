import { Accessor } from "solid-js";
import { SetStoreFunction } from "solid-js/store";
import {
  Clan,
  ClanMember,
  ClanMethods,
  Clans,
  ClansMethods,
  Service,
  ServiceInstances,
  ServiceInstancesMethods,
} from "..";
import { mapObjectValues } from "@/src/util";

export type ServiceInstanceEntity = {
  readonly data: ServiceInstanceEntityData;
};
export type ServiceInstanceEntityData = {
  readonly name: string;
  readonly roles: Record<string, ServiceInstanceRoleEntity>;
};

export type ServiceInstance = Omit<ServiceInstanceEntity, "data"> & {
  readonly clan: Clan;
  readonly service: Service;
  data: ServiceInstanceData;
  readonly isActive: boolean;
};

export type ServiceInstanceData = Omit<ServiceInstanceEntityData, "roles"> & {
  roles: Record<string, ServiceInstanceRole>;
};

export type ServiceInstanceRoleEntity = {
  readonly id: string;
  readonly settings: Record<string, unknown>;
  readonly machines: string[];
  readonly tags: string[];
};

export type ServiceInstanceRole = Omit<
  ServiceInstanceRoleEntity,
  "settings"
> & {
  settings: Record<string, unknown>;
  members: ClanMember[];
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

export function toServiceInstance(
  instance: ServiceInstanceEntity,
  service: Accessor<Service>,
): ServiceInstance {
  return {
    ...instance,
    data: {
      ...instance.data,
      roles: mapObjectValues(instance.data.roles, ([roleId, role]) => ({
        ...role,
        members: [
          ...role.machines.map((name) => ({
            type: "machine" as const,
            name,
          })),
          ...role.tags.map((name) => ({ type: "tag" as const, name })),
        ].sort((a, b) => a.name.localeCompare(b.name)),
        get machines() {
          return this.members
            .filter(({ type }) => type === "machine")
            .map(({ name }) => name);
        },
        get tags() {
          return this.members
            .filter(({ type }) => type === "tag")
            .map(({ name }) => name);
        },
      })),
    },
    get clan() {
      return service().clan;
    },
    get service() {
      return service();
    },
    get isActive() {
      return (
        this.data.name ===
        this.clan.serviceInstances.activeServiceInstance?.data.name
      );
    },
  };
}
