import { mapObjectValues } from "@/src/util";
import { ServiceInstanceDataEntity } from "../../service";
import client from "./client-call";

export async function createServiceInstance(
  data: ServiceInstanceDataEntity,
  serviceId: string,
  clanId: string,
): Promise<void> {
  await client.post("create_service_instance", {
    body: {
      flake: {
        identifier: clanId,
      },
      module_ref: {
        name: serviceId,
        input: null,
      },
      roles: mapObjectValues(data.roles, ([, role]) => ({
        machines: Object.fromEntries(
          role.machines.map((machineId) => [machineId, {}]),
        ),
        tags: Object.fromEntries(role.tags.map((tag) => [tag, {}])),
      })),
    },
  });
}

export async function updateServiceInstanceData(
  data: ServiceInstanceDataEntity,
  clanId: string,
): Promise<void> {
  await client.post("set_service_instance", {
    body: {
      flake: {
        identifier: clanId,
      },
      instance_ref: data.name,
      roles: mapObjectValues(data.roles, ([, role]) => ({
        settings: role.settings,
        machines: Object.fromEntries(
          role.machines.map((machineId) => [machineId, {}]),
        ),
        tags: Object.fromEntries(role.tags.map((tag) => [tag, {}])),
      })),
    },
  });
}
