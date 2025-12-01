import { ClanData, ClanMeta, Tags } from "../../Clan";
import client from "./client-call";

export async function getClanDir(): Promise<string> {
  const res = await client.get("get_clan_folder");
  return res.data.identifier;
}
// TODO: make this one API call only
export async function getClan(id: string): Promise<ClanMeta> {
  // TODO: make this a GET instead
  const [clanRes, schemaRes] = await Promise.all([
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
    data: clanRes.data,
    schema: schemaRes.data,
  } as ClanMeta;
}

// TODO: make this one API call only
export async function getClans(ids: string[]): Promise<ClanMeta[]> {
  return await Promise.all(ids.map(async (id) => await getClan(id)));
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
        meta: data,
      },
    },
  });
}

// TODO: make this one API call only
// TODO: allow users to select a template
export async function createClan(
  path: string,
  data: ClanData,
): Promise<ClanMeta> {
  await client.post("create_clan", {
    body: {
      opts: {
        dest: path,
        template: "minimal",
        initial: data,
      },
    },
  });

  const [schemaRes] = await Promise.all([
    client.post("get_clan_details_schema", {
      body: {
        flake: {
          identifier: path,
        },
      },
    }),
    client.post("create_service_instance", {
      body: {
        flake: {
          identifier: path,
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
        flake_dir: path,
      },
    }),
  ]);

  return {
    id: path,
    data,
    schema: schemaRes.data,
  };
}

export async function getTags(clanId: string): Promise<Tags> {
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
