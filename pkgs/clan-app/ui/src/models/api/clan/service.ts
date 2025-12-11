import { mapObjectValues } from "@/src/util";
import { ServiceInstance } from "../../service";
import client from "./client-call";

export async function createServiceInstance(
  instance: ServiceInstance,
): Promise<void> {
  await client.post("create_service_instance", {
    body: {
      flake: {
        identifier: instance.clan.id,
      },
      module_ref: {
        name: instance.service.id,
        input: instance.service.source,
      },
      roles: mapObjectValues(instance.data.roles, ([roleId, role]) => ({
        machines: Object.fromEntries(
          role.machines.map((machineId) => [machineId, {}]),
        ),
        tags: role.tags,
      })),
    },
  });
}
