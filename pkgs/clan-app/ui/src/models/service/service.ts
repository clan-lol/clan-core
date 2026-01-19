import { JSONSchema } from "json-schema-typed/draft-2020-12";
import { Clan, ServiceInstance } from "..";
import { ServiceInstanceOutput } from "./instance";
import { Accessor } from "solid-js";
import { mapObjectValues } from "@/util";

export type ServiceOutput = {
  readonly description: string;
  readonly isCore: boolean;
  readonly source: string | null;
  readonly roles: Record<string, ServiceRoleOutput>;
  readonly rolesSchema: Record<string, JSONSchema>;
  readonly instances: ServiceInstanceOutput[];
};
export type ServiceRoleOutput = {
  readonly description: string;
};

export type Service = Omit<ServiceOutput, "roles" | "instances"> & {
  readonly clan: Clan;
  readonly id: string;
  readonly roles: ServiceRoles;
  readonly instances: ServiceInstance[];
};
export type ServiceRoles = {
  all: Record<string, ServiceRole>;
  sorted: ServiceRole[];
};
export type ServiceRole = ServiceRoleOutput & {
  readonly id: string;
};

export function createServiceFromOutput(
  id: string,
  output: ServiceOutput,
  clan: Accessor<Clan>,
): Service {
  return {
    ...output,
    id,
    get clan(): Clan {
      return clan();
    },
    roles: {
      all: mapObjectValues(output.roles, ([id, role]) => ({
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
