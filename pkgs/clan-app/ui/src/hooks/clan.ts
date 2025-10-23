import { callApi } from "@/src/hooks/api";
import { addClanURI, setActiveClanURI } from "@/src/stores/clan";
import { Params, Navigator, useParams, useSearchParams } from "@solidjs/router";

export const encodeBase64 = (value: string) => window.btoa(value);
const decodeBase64 = (value: string) => window.atob(value);

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
  id: string;
  module: {
    name: string;
    input?: string | null | undefined;
  };
}) => {
  const { clanURI, id, module } = props;

  const moduleName = encodeBase64(module.name);
  const idEncoded = encodeBase64(id);

  const result =
    buildClanPath(clanURI) +
    `/services/${moduleName}/${idEncoded}` +
    (module.input ? `?input=${module.input}` : "");

  return result;
};

export const useServiceParams = () => {
  const params = useParams<{
    name?: string;
    id?: string;
  }>();

  const [search] = useSearchParams<{ input?: string }>();

  if (!params.name || !params.id) {
    console.error("Service params not found", params, window.location.pathname);
    throw new Error("Service params not found");
  }

  return {
    name: decodeBase64(params.name),
    id: decodeBase64(params.id),
    input: search.input,
  };
};

export const navigateToClan = (navigate: Navigator, clanURI: string) => {
  const path = buildClanPath(clanURI);
  console.log("Navigating to clan", clanURI, path);
  navigate(path);
};

export const navigateToOnboarding = (navigate: Navigator, addClan: boolean) =>
  navigate(`/${addClan ? "?addClan=true" : ""}`);

const navigateToMachine = (
  navigate: Navigator,
  clanURI: string,
  name: string,
) => {
  const path = buildMachinePath(clanURI, name);
  console.log("Navigating to machine", clanURI, name, path);
  navigate(path);
};

const clanURIParam = (params: Params) => {
  try {
    return decodeBase64(params.clanURI);
  } catch (e) {
    console.error("Failed to decode clan URI:", params.clanURI, e);
    throw new Error("Invalid clan URI");
  }
};

export const useClanURI = () => clanURIParam(useParams());

const machineNameParam = (params: Params) => {
  return params.machineName;
};

const inputParam = (params: Params) => params.input;
const nameParam = (params: Params) => params.name;
const idParam = (params: Params) => params.id;

export const useMachineName = (): string => machineNameParam(useParams());
const useInputParam = (): string => inputParam(useParams());
const useNameParam = (): string => nameParam(useParams());

const maybeUseIdParam = (): string | null => {
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
