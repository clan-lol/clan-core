import { callApi } from "@/src/hooks/api";
import { addClanURI, setActiveClanURI } from "@/src/stores/clan";
import { Params, Navigator, useParams } from "@solidjs/router";

export const selectClanFolder = async () => {
  const req = callApi("get_clan_folder", {});
  const res = await req.result;

  if (res.status === "error") {
    throw new Error(res.errors[0].message);
  }

  if (res.status === "success" && res.data) {
    const { identifier: uri } = res.data;
    addClanURI(uri);
    setActiveClanURI(uri);
    return uri;
  }

  throw new Error("Illegal state exception");
};

export const navigateToClan = (navigate: Navigator, uri: string) => {
  navigate("/clans/" + window.btoa(uri));
};

export const clanURIParam = (params: Params) => {
  return window.atob(params.clanURI);
};

export function useClanURI(opts: { force: true }): string;
export function useClanURI(opts: { force: boolean }): string | null;
export function useClanURI(
  opts: { force: boolean } = { force: false },
): string | null {
  const maybe = () => {
    const params = useParams();
    if (!params.clanURI) {
      return null;
    }
    const clanURI = clanURIParam(params);
    if (!clanURI) {
      throw new Error(
        "Could not decode clan URI from params: " + params.clanURI,
      );
    }
    return clanURI;
  };

  const uri = maybe();
  if (!uri && opts.force) {
    throw new Error(
      "ClanURI is not set. Use this function only within contexts, where clanURI is guaranteed to have been set.",
    );
  }
  return uri;
}
