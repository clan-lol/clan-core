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

export type ServiceInstanceEntity = {
  data: ServiceInstanceEntityData;
};
export type ServiceInstanceEntityData = {
  name: string;
  roles: Record<string, ServiceInstanceRoleEntity>;
};

export type ServiceInstance = Omit<ServiceInstanceEntity, "data"> & {
  readonly clan: Clan;
  readonly service: Service;
  data: ServiceInstanceData;
  readonly isActive: boolean;
  readonly isNew: boolean;
  readonly index: number;
};

export type ServiceInstanceData = Omit<ServiceInstanceEntityData, "roles"> & {
  roles: Record<string, ServiceInstanceRole>;
};

export type ServiceInstanceRoleEntity = {
  readonly id: string;
  settings: Record<string, unknown>;
  machines: string[];
  tags: string[];
};

export type ServiceInstanceRole = Omit<
  ServiceInstanceRoleEntity,
  "machines" | "tags"
> & {
  readonly machines: string[];
  readonly tags: string[];
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
      roles: Object.fromEntries(
        Object.entries(instance.data.roles).map(([roleId, role]) => [
          roleId,
          {
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
          },
        ]),
      ),
    },
    get clan() {
      return service().clan;
    },
    get service() {
      return service();
    },
    get isActive() {
      const i = this.clan.serviceInstances.activeIndex;
      if (i === undefined || i === -1) {
        return false;
      }
      return this.data.name === this.clan.serviceInstances.all[i].data.name;
    },
    get isNew() {
      return this.index === -1;
    },
    get index() {
      return this.clan.serviceInstances.all.findIndex(
        (instance) => this.data.name === instance.data.name,
      );
    },
  };
}
