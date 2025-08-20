import { callApi } from "@/src/hooks/api";
import { addClanURI, setActiveClanURI } from "@/src/stores/clan";
import { Params, Navigator, useParams } from "@solidjs/router";

export const encodeBase64 = (value: string) => window.btoa(value);
export const decodeBase64 = (value: string) => window.atob(value);

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

export const buildClanPath = (clanURI: string) => {
  return "/clans/" + encodeBase64(clanURI);
};

export const buildMachinePath = (clanURI: string, name: string) =>
  buildClanPath(clanURI) + "/machines/" + name;

export const navigateToClan = (navigate: Navigator, clanURI: string) => {
  const path = buildClanPath(clanURI);
  console.log("Navigating to clan", clanURI, path);
  navigate(path);
};

export const navigateToOnboarding = (navigate: Navigator, addClan: boolean) =>
  navigate(`/${addClan ? "?addClan=true" : ""}`);

export const navigateToMachine = (
  navigate: Navigator,
  clanURI: string,
  name: string,
) => {
  const path = buildMachinePath(clanURI, name);
  console.log("Navigating to machine", clanURI, name, path);
  navigate(path);
};

export const clanURIParam = (params: Params) => {
  try {
    return decodeBase64(params.clanURI);
  } catch (e) {
    console.error("Failed to decode clan URI:", params.clanURI, e);
    throw new Error("Invalid clan URI");
  }
};

export const useClanURI = () => clanURIParam(useParams());

export const machineNameParam = (params: Params) => {
  return params.machineName;
};

export const useMachineName = (): string => machineNameParam(useParams());

export const maybeUseMachineName = (): string | null => {
  const params = useParams();
  if (params.machineName === undefined) {
    return null;
  }
  return machineNameParam(params);
};
