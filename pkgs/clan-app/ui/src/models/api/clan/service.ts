import { mapObjectValues } from "@/src/util";
import { ServiceInstanceEntityData } from "../../service";
import client from "./client-call";

export async function createServiceInstance(
  data: ServiceInstanceEntityData,
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
      },
      roles: mapObjectValues(data.roles, ([, role]) => ({
        machines: Object.fromEntries(
          role.machines.map((machineId) => [machineId, {}]),
        ),
        tags: role.tags,
      })),
    },
  });
}
