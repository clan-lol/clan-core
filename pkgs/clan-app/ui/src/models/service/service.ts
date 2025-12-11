import { JSONSchema } from "json-schema-typed/draft-2020-12";
import { Clan, Clans, ClansMethods, ServiceInstance } from "..";
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
  readonly instances: ServiceInstance[];
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
    const service = clan().services.find((service) => service.id === id);
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
