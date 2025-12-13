import { JSONSchema } from "json-schema-typed/draft-2020-12";
import { Clan, ServiceInstance } from "..";
import { ServiceInstanceEntity, toServiceInstance } from "./instance";
import { Accessor } from "solid-js";

export type ServiceEntity = {
  readonly id: string;
  readonly description: string;
  readonly isCore: boolean;
  readonly source: string | null;
  readonly roles: Record<string, ServiceRole>;
  readonly rolesSchema: Record<string, JSONSchema>;
  readonly instances: ServiceInstanceEntity[];
};

export type Service = Omit<ServiceEntity, "instances"> & {
  readonly clan: Clan;
  // clans, machines and services all use a Record<string, ...> type, instances
  // doesn't follow suit because an instance doesn't have a stable id, using a
  // record requires the key to be updated as well when the id (instance name)
  // is updated
  instances: ServiceInstance[];
};

export type ServiceRole = {
  readonly description: string;
};

export function toService(
  entity: ServiceEntity,
  clan: Accessor<Clan>,
): Service {
  const service = () => {
    const { id } = entity;
    const service = clan().services.all[id];
    if (!service) {
      throw new Error(`Service does not exist: ${id}`);
    }
    return service;
  };
  return {
    ...entity,
    get clan(): Clan {
      return clan();
    },
    instances: entity.instances.map((instance) =>
      toServiceInstance(instance, service),
    ),
  };
}
