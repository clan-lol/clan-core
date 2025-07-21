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

export const buildMachinePath = (clanURI: string, machineID: string) => {
  return (
    "/clans/" + encodeBase64(clanURI) + "/machines/" + encodeBase64(machineID)
  );
};

export const navigateToClan = (navigate: Navigator, clanURI: string) => {
  const path = buildClanPath(clanURI);
  console.log("Navigating to clan", clanURI, path);
  navigate(path);
};

export const navigateToMachine = (
  navigate: Navigator,
  clanURI: string,
  machineID: string,
) => {
  const path = buildMachinePath(clanURI, machineID);
  console.log("Navigating to machine", clanURI, machineID, path);
  navigate(path);
};

export const clanURIParam = (params: Params) => {
  return decodeBase64(params.clanURI);
};

export const useClanURI = () => clanURIParam(useParams());

export const machineIDParam = (params: Params) => {
  return decodeBase64(params.machineID);
};

export const useMachineID = (): string => {
  const params = useParams();
  return machineIDParam(params);
};
