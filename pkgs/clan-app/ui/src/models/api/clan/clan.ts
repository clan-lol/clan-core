import {
  ClanData,
  ClanEntity,
  ClanMetaData,
  ClanMetaEntity,
  ClanNewEntity,
  ClansEntity,
} from "../../clan";
import { MachineData } from "../../Machine";
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
  const [clan, dataSchema] = await Promise.all([
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
  ]);
  return {
    id,
    data: clan.data as ClanData,
    dataSchema: dataSchema.data,
    machines: [],
    services: [],
    globalTags: { regular: [], special: [] },
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
export async function createClan(data: ClanNewEntity): Promise<ClanEntity> {
  await client.post("create_clan", {
    body: {
      opts: {
        dest: data.id,
        template: "minimal",
        initial: data.data,
      },
    },
  });

  const [schemaRes] = await Promise.all([
    client.post("get_clan_details_schema", {
      body: {
        flake: {
          identifier: data.id,
        },
      },
    }),
    client.post("create_service_instance", {
      body: {
        flake: {
          identifier: data.id,
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
        flake_dir: data.id,
      },
    }),
  ]);

  return {
    id: data.id,
    data: data.data,
    dataSchema: {},
    machines: [],
    services: [],
    globalTags: { regular: [], special: [] },
  };
}

export async function getAllTags(clanId: string): Promise<Tags> {
  const res = await client.post("list_tags", {
    body: {
      flake: {
        identifier: clanId,
      },
    },
  });
  return {
    regular: res.data.options,
    special: res.data.special,
  };
}
