import { JSONSchema } from "json-schema-typed/draft-2020-12";
import client from "./client-call";
import {
  ClanData,
  ClanOutput,
  ClanMetaOutput,
  ClanDataOutput,
} from "../../clan/clan";
import {
  MachineEntity,
  MachinePositions,
  machinePositions,
} from "../../machine/machine";
import { asyncMapObjectValues, mapObjectValues } from "@/src/util";
import { ServiceEntity, ServiceRoleEntity } from "../../service/service";

// TODO: make this one API call only
export async function getClans(
  ids: string[],
  activeIndex: number,
): Promise<(ClanOutput | ClanMetaOutput)[]> {
  return await Promise.all(
    ids.map(async (id, i) => {
      if (i === activeIndex) {
        return await getClan(id);
      }
      return await getClanMeta(id);
    }),
  );
}
export async function getClanMeta(id: string): Promise<ClanMetaOutput> {
  const clan = await client.post("get_clan_details", {
    body: {
      flake: {
        identifier: id,
      },
    },
  });
  return {
    id,
    data: {
      name: clan.data.name,
      description: clan.data.description || "",
    },
  };
}

export async function getClan(id: string): Promise<ClanOutput> {
  const [
    clanRes,
    dataSchemaRes,
    machinesRes,
    tagsRes,
    servicesRes,
    serviceInstancesRes,
  ] = await Promise.all([
    client.post("get_clan_details", {
      body: {
        flake: {
          identifier: id,
        },
      },
    }),
    client.post("get_clan_details_schema", {
      body: {
        flake: {
          identifier: id,
        },
      },
    }),
    client.post("list_machines", {
      body: {
        flake: {
          identifier: id,
        },
      },
    }),
    client.post("list_tags", {
      body: {
        flake: {
          identifier: id,
        },
      },
    }),
    client.post("list_service_modules", {
      body: {
        flake: {
          identifier: id,
        },
      },
    }),
    client.post("list_service_instances", {
      body: {
        flake: {
          identifier: id,
        },
      },
    }),
  ]);
  const machines: Record<string, MachineEntity> = await asyncMapObjectValues(
    machinesRes.data,
    async ([machineId, machine]) => {
      const [stateRes, schemaRes] = await Promise.all([
        client.post("get_machine_state", {
          body: {
            machine: {
              name: machineId,
              flake: {
                identifier: id,
              },
            },
          },
        }),
        client.post("get_machine_fields_schema", {
          body: {
            machine: {
              name: machineId,
              flake: {
                identifier: id,
              },
            },
          },
        }),
      ]);

      let mp: MachinePositions;
      if (!machinePositions[id]) {
        mp = new MachinePositions({});
        machinePositions[id] = mp;
      } else {
        mp = machinePositions[id];
      }
      return {
        id: machineId,
        data: {
          ...machine.data,
          position: mp.getOrSetPosition(machineId),
        },
        dataSchema: schemaRes.data,
        status: stateRes.data.status,
      };
    },
  );
  const services: Record<string, ServiceEntity> = Object.fromEntries(
    servicesRes.data.modules.map((service) => [
      service.usage_ref.name,
      {
        id: service.usage_ref.name,
        isCore: service.native,
        description: service.info.manifest.description,
        source: service.usage_ref.input ?? null,
        roles: service.info.roles as Record<string, ServiceRoleEntity>,
        rolesSchema: {},
        instances: service.instance_refs.map((instanceName) => {
          const instance = serviceInstancesRes.data[instanceName];
          return {
            data: {
              name: instanceName,
              roles: mapObjectValues(instance.roles, ([, role]) => ({
                settings: role.settings as Record<string, unknown>,
                settingsSchema: {} as JSONSchema,
                machines: Object.entries(machinesRes.data)
                  .filter(([, machine]) =>
                    machine.instance_refs?.includes(instanceName),
                  )
                  .map(([id]) => id),
                tags: Object.keys(role.tags ?? {}),
              })),
            },
          };
        }),
      },
    ]),
  );
  return {
    id,
    data: {
      name: clanRes.data.name,
      description: clanRes.data.description || "",
      domain: clanRes.data.domain,
    },
    dataSchema: dataSchemaRes.data,
    machines,
    services,
    globalTags: {
      regular: tagsRes.data.options,
      special: tagsRes.data.special,
    },
  };
}

// TODO: backend should provide an API that allows partial update
export async function updateClanData(
  clanId: string,
  data: ClanData,
): Promise<void> {
  await client.post("set_clan_details", {
    body: {
      options: {
        flake: {
          identifier: clanId,
        },
        meta: {
          name: data.name,
          description: data.description,
          domain: data.domain,
        },
      },
    },
  });
}

// TODO: make this one API call only
// TODO: allow users to select a template
export async function createClan(
  id: string,
  data: ClanData,
): Promise<ClanDataOutput> {
  const res = await client.post("create_clan", {
    body: {
      opts: {
        dest: id,
        template: "minimal",
        initial: data,
      },
    },
  });

  await Promise.all([
    client.post("create_service_instance", {
      body: {
        flake: {
          identifier: id,
        },
        module_ref: {
          name: "admin",
          input: "clan-core",
        },
        roles: {
          default: {
            tags: {
              all: {},
            },
          },
        },
      },
    }),
    client.post("create_secrets_user", {
      body: {
        flake_dir: id,
      },
    }),
  ]);

  return {
    name: res.data.name,
    description: res.data.description || "",
    domain: res.data.domain,
  };
}
