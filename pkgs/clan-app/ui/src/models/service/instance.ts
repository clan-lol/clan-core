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
import { DeepImmutable, DeepRequired, mapObjectValues } from "@/util";

export type ServiceInstanceOutput = {
  readonly data: ServiceInstanceDataOutput;
};

export type ServiceInstance = Omit<ServiceInstanceOutput, "data"> & {
  readonly clan: Clan;
  readonly service: Service;
  data: ServiceInstanceData;
  readonly isActive: boolean;
};

// FIXME: all properties should be optional,
// backend should figure out filling in missing data
export type ServiceInstanceDataChange = {
  name: string;
  roles: Record<string, ServiceInstanceRoleChange>;
};
export type ServiceInstanceData = {
  name: string;
  roles: ServiceInstanceRoles;
};
export type ServiceInstanceDataOutput = DeepImmutable<
  DeepRequired<ServiceInstanceDataChange>
>;

export type ServiceInstanceRoles = {
  all: Record<string, ServiceInstanceRole>;
  readonly sorted: ServiceInstanceRole[];
};

export type ServiceInstanceRoleChange = {
  settings?: Record<string, unknown>;
  machines?: string[];
  tags?: string[];
};
export type ServiceInstanceRole = {
  readonly id: string;
  readonly members: ClanMember[];
} & DeepRequired<ServiceInstanceRoleChange>;

export type ServiceInstanceRoleOutput = DeepImmutable<
  DeepRequired<ServiceInstanceRoleChange>
>;

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

export function createServiceInstanceFromOutput({
  output,
  service,
  clan,
}: {
  output: ServiceInstanceOutput;
  service: Accessor<Service>;
  clan: Accessor<Clan>;
}): ServiceInstance {
  return {
    ...output,
    data: {
      ...output.data,
      roles: {
        all: mapObjectValues(output.data.roles, ([roleId, role]) => ({
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
  };
}
