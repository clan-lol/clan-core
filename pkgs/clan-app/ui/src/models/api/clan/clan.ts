import { JSONSchema } from "json-schema-typed/draft-2020-12";
import client from "./client-call";
import {
  ClanData,
  ClanEntity,
  ClanMetaData,
  ClanMetaEntity,
  NewClanEntity,
} from "../../clan/clan";
import {
  MachineData,
  MachinePositions,
  machinePositions,
} from "../../machine/machine";
import { ServiceRole } from "../../service";

// TODO: make this one API call only
export async function getClans(
  ids: string[],
  activeIndex: number,
): Promise<(ClanEntity | ClanMetaEntity)[]> {
  return await Promise.all(
    ids.map(async (id, i) => {
      if (i === activeIndex) {
        return await getClan(id);
      }
      return await getClanMeta(id);
    }),
  );
}
export async function getClanMeta(id: string): Promise<ClanMetaEntity> {
  const clan = await client.post("get_clan_details", {
    body: {
      flake: {
        identifier: id,
      },
    },
  });
  return {
    id,
    data: clan.data as ClanMetaData,
  };
}

export async function getClan(id: string): Promise<ClanEntity> {
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
  const machines = await Promise.all(
    Object.entries(machinesRes.data).map(async ([machineId, machine]) => {
      const [state, schema] = await Promise.all([
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
        data: machine.data as MachineData,
        dataSchema: schema.data,
        status: state.data.status,
        position: mp.getOrSetPosition(machineId),
      };
    }),
  );
  const services: ClanEntity["services"] = servicesRes.data.modules.map(
    (service) => ({
      id: service.usage_ref.name,
      isCore: service.native,
      description: service.info.manifest.description,
      source: service.usage_ref.input!,
      roles: service.info.roles as Record<string, ServiceRole>,
      rolesSchema: {},
      instances: service.instance_refs.map((instanceName) => {
        const instance = serviceInstancesRes.data[instanceName];
        return {
          data: {
            name: instanceName,
            roles: Object.fromEntries(
              Object.entries(instance.roles).map(([roleId, role]) => [
                roleId,
                {
                  id: roleId,
                  settings: role.settings as Record<string, unknown>,
                  settingsSchema: {} as JSONSchema,
                  machines: Object.keys(role.machines!),
                  tags: Object.keys(role.tags!),
                },
              ]),
            ),
          },
        };
      }),
    }),
  );
  return {
    id,
    data: clanRes.data as ClanData,
    dataSchema: dataSchemaRes.data,
    machines,
    services,
    globalTags: {
      regular: tagsRes.data.options,
      special: tagsRes.data.special,
    },
  };
}

export async function pickClanDir(): Promise<string> {
  const res = await client.get("get_clan_folder");
  return res.data.identifier;
}

// TODO: backend should provide an API that allows partial update
export async function updateClanData(
  clanId: string,
  data: Partial<ClanData>,
): Promise<void> {
  await client.post("set_clan_details", {
    body: {
      options: {
        flake: {
          identifier: clanId,
        },
        meta: data as ClanData,
      },
    },
  });
}

// TODO: make this one API call only
// TODO: allow users to select a template
export async function createClan(entity: NewClanEntity): Promise<ClanEntity> {
  await client.post("create_clan", {
    body: {
      opts: {
        dest: entity.id,
        template: "minimal",
        initial: entity.data,
      },
    },
  });

  const [dataSchema, tags] = await Promise.all([
    client.post("get_clan_details_schema", {
      body: {
        flake: {
          identifier: entity.id,
        },
      },
    }),
    client.post("list_tags", {
      body: {
        flake: {
          identifier: entity.id,
        },
      },
    }),
    client.post("create_service_instance", {
      body: {
        flake: {
          identifier: entity.id,
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
        flake_dir: entity.id,
      },
    }),
  ]);

  return {
    id: entity.id,
    data: entity.data,
    dataSchema: dataSchema.data,
    machines: [],
    services: [],
    globalTags: {
      regular: tags.data.options,
      special: tags.data.special,
    },
  };
}
