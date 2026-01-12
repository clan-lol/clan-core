import { JSONSchema } from "json-schema-typed/draft-2020-12";
import { Clan, ServiceInstance } from "..";
import { ServiceInstanceEntity } from "./instance";
import { Accessor } from "solid-js";
import { mapObjectValues } from "@/src/util";

export type ServiceEntity = {
  readonly description: string;
  readonly isCore: boolean;
  readonly source: string | null;
  readonly roles: Record<string, ServiceRoleEntity>;
  readonly rolesSchema: Record<string, JSONSchema>;
  readonly instances: ServiceInstanceEntity[];
};
export type ServiceRoleEntity = {
  readonly description: string;
};

export type Service = Omit<ServiceEntity, "roles" | "instances"> & {
  readonly clan: Clan;
  readonly id: string;
  readonly roles: ServiceRoles;
  readonly instances: ServiceInstance[];
};
export type ServiceRoles = {
  all: Record<string, ServiceRole>;
  sorted: ServiceRole[];
};
export type ServiceRole = ServiceRoleEntity & {
  readonly id: string;
};

export function createService(
  id: string,
  entity: ServiceEntity,
  clan: Accessor<Clan>,
): Service {
  return {
    ...entity,
    id,
    get clan(): Clan {
      return clan();
    },
    roles: {
      all: mapObjectValues(entity.roles, ([id, role]) => ({
        ...role,
        id,
      })),
      get sorted() {
        return Object.values(this.all).sort((a, b) => a.id.localeCompare(b.id));
      },
    },
    get instances() {
      return clan().serviceInstances.sorted.filter(
        (instance) => instance.service.id === this.id,
      );
    },
  };
}
