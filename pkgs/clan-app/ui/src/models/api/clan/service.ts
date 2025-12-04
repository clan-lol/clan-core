import client from "@/src/models/api/clan/client-call";
import { ServiceMeta, ServiceRoleSchema } from "../../Service";

export async function getServices(clanId: string): Promise<ServiceMeta[]> {
  const res = await client.post("list_service_modules", {
    body: {
      flake: {
        identifier: clanId,
      },
    },
  });
  return res.data as ServiceMeta[];
}

// export async function getServiceInstances(
//   clanId: string,
// ): Promise<Record<string, ServiceInstanceMeta>> {
//   const res = await client.post("list_service_instances", {
//     body: {
//       flake: {
//         identifier: clanId,
//       },
//     },
//   });
//   return res.data as Record<string, ServiceInstanceMeta>;
// }

export async function getServiceRolesSchema(
  serviceId: string,
  clanId: string,
): Promise<ServiceRoleSchema[]> {
  return [];
}
