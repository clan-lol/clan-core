import {
  ClanData,
  ClanEntity,
  ClanMetaData,
  ClanMetaEntity,
  ClanNewEntity,
  ClansEntity,
} from "../../clan";
import { MachineEntity } from "../../machine";
import client from "./client-call";

// TODO: make this one API call only
export async function getClans(
  ids: string[],
  activeIndex: number,
): Promise<ClansEntity> {
  return {
    all: await Promise.all(
      ids.map(async (id, i) => {
        if (i === activeIndex) {
          return await getClan(id);
        }
        return await getClanMeta(id);
      }),
    ),
    activeIndex,
  };
}
export async function getClanMeta(id: string): Promise<ClanMetaEntity> {
  // TODO: make this a GET instead
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
  const [clan, dataSchema, rawMachines, tags] = await Promise.all([
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
  ]);
  const machines = await Promise.all(
    Object.entries(rawMachines.data).map(async ([machineId, machine]) => {
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
      return {
        id: machineId,
        data: machine.data,
        dataSchema: schema.data,
        serviceInstances: machine.instance_refs,
        status: state.data.status,
      } as MachineEntity;
    }),
  );
  return {
    id,
    data: clan.data as ClanData,
    dataSchema: dataSchema.data,
    machines,
    services: [],
    globalTags: {
      regular: tags.data.options,
      special: tags.data.special,
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
export async function createClan(entity: ClanNewEntity): Promise<ClanEntity> {
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
