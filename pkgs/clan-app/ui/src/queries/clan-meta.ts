import { useQuery } from "@tanstack/solid-query";
import { callApi } from "@/src/api";
import { activeClanURI, removeClanURI } from "@/src/stores/clan";

export const clanMetaQuery = (uri: string | undefined = undefined) =>
  useQuery(() => {
    const clanURI = uri || activeClanURI();
    const enabled = !!clanURI;

    return {
      enabled,
      queryKey: [clanURI, "meta"],
      queryFn: async () => {
        console.log("fetching clan meta", clanURI);

        const result = await callApi("show_clan_meta", {
          flake: { identifier: clanURI! },
        });

        console.log("result", result);

        if (result.status === "error") {
          // check if the clan directory no longer exists
          // remove from the clan list if not
          result.errors.forEach((error) => {
            if (error.description === "clan directory does not exist") {
              removeClanURI(clanURI!);
            }
          });

          throw new Error("Failed to fetch data");
        }

        return result.data;
      },
    };
  });
