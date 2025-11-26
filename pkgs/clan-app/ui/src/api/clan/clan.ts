import client from "@api/clan/client";

export async function getClanDir(): Promise<string> {
  const res = await client.get("get_clan_folder");
  return res.data.identifier;
}

export interface ClanData {
  name: string;
  description?: string;
}

export interface ClanMeta {
  id: string;
  data: ClanData;
  schema: Record<string, { readonly: boolean; reason: string | null }>;
}

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

// TODO: create a backend API that retrives multiple clans in one go
export async function getClans(ids: string[]): Promise<ClanMeta[]> {
  return await Promise.all(ids.map(async (id) => await getClan(id)));
}

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
