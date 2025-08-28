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

export const buildServicePath = (props: {
  clanURI: string;
  machineName?: string;
  id: string;
  module: {
    input?: string | null | undefined;
    name: string;
  };
}) => {
  const { clanURI, machineName, id, module } = props;
  const result =
    (machineName
      ? buildMachinePath(clanURI, machineName)
      : buildClanPath(clanURI)) +
    `/services/${module.input ?? "clan"}/${module.name}`;
  return id == module.name ? result : result + "/" + id;
};

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

export const inputParam = (params: Params) => params.input;
export const nameParam = (params: Params) => params.name;
export const idParam = (params: Params) => params.id;

export const useMachineName = (): string => machineNameParam(useParams());
export const useInputParam = (): string => inputParam(useParams());
export const useNameParam = (): string => nameParam(useParams());

export const maybeUseIdParam = (): string | null => {
  const params = useParams();
  if (params.id === undefined) {
    return null;
  }
  return idParam(params);
};

export const maybeUseMachineName = (): string | null => {
  const params = useParams();
  if (params.machineName === undefined) {
    return null;
  }
  return machineNameParam(params);
};
