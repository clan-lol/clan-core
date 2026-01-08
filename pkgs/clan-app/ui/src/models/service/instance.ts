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
  useClanContext,
  useClansContext,
  useServiceInstancesContext,
} from "..";
import { mapObjectValues } from "@/src/util";

export type ServiceInstanceEntity = {
  readonly data: ServiceInstanceDataEntity;
};
export type ServiceInstanceDataEntity = {
  readonly name: string;
  readonly roles: Record<string, ServiceInstanceRoleEntity>;
};

export type ServiceInstance = Omit<ServiceInstanceEntity, "data"> & {
  readonly clan: Clan;
  readonly service: Service;
  data: ServiceInstanceData;
  readonly isActive: boolean;
  // readonly isNew: boolean;
};

export type ServiceInstanceData = Omit<ServiceInstanceDataEntity, "roles"> & {
  roles: ServiceInstanceRoles;
};

export type ServiceInstanceRoleEntity = {
  readonly settings: Record<string, unknown>;
  readonly machines: string[];
  readonly tags: string[];
};

export type ServiceInstanceRoles = {
  all: Record<string, ServiceInstanceRole>;
  readonly sorted: ServiceInstanceRole[];
};
export type ServiceInstanceRole = Omit<
  ServiceInstanceRoleEntity,
  "settings"
> & {
  readonly id: string;
  settings: Record<string, unknown>;
  members: ClanMember[];
};

export type ServiceInstanceMethods = {
  setServiceInstance: SetStoreFunction<ServiceInstance>;
  activateServiceInstance(this: void): void;
};
export function createInstanceMethods(
  instance: Accessor<ServiceInstance>,
  [, { activateServiceInstance }]: readonly [
    Accessor<ServiceInstances>,
    ServiceInstancesMethods,
  ],
  [clan, { setClan }]: readonly [Accessor<Clan>, ClanMethods],
  _: readonly [Clans, ClansMethods],
): ServiceInstanceMethods {
  const setInstance: SetStoreFunction<ServiceInstance> = (
    ...args: unknown[]
  ) => {
    const i = clan().serviceInstances.all.indexOf(instance());
    if (i === -1) {
      throw new Error(
        `This service instance does not belong to the known service instance: ${instance().data.name}`,
      );
    }
    // @ts-expect-error ...args won't infer properly for overloaded functions
    setClan("serviceInstances", "all", i, ...args);
  };
  const self: ServiceInstanceMethods = {
    setServiceInstance: setInstance,
    activateServiceInstance() {
      activateServiceInstance(instance());
    },
  };
  return self;
}

export function createServiceInstance({
  entity,
  service,
  clan,
}: {
  entity: ServiceInstanceEntity;
  service: Accessor<Service>;
  clan: Accessor<Clan>;
}): ServiceInstance {
  return {
    ...entity,
    data: {
      ...entity.data,
      roles: {
        all: mapObjectValues(entity.data.roles, ([roleId, role]) => ({
          ...role,
          id: roleId,
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
        get sorted() {
          return Object.values(this.all).sort((a, b) =>
            a.id.localeCompare(b.id),
          );
        },
      },
    },
    get service() {
      return service();
    },
    get clan() {
      return clan();
    },
    get isActive() {
      return this.service.clan.serviceInstances.activeServiceInstance === this;
    },
    // get isNew() {
    //   return !!instancePath(this.data.name, this.service.clan.services.all);
    // },
  };
}

// function instancePath(
//   instanceName: string,
//   services: Record<string, Service>,
// ): readonly [string, number] | null {
//   for (const [, service] of Object.entries(services)) {
//     for (const [i, instance] of service.instances.entries()) {
//       if (instance.data.name === instanceName) {
//         return [service.id, i];
//       }
//     }
//   }
//   return null;
// }
