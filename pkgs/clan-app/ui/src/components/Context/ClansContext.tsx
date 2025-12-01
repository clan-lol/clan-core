import { ClanList } from "@/src/models/Clan";
import { AccessorWithLatest } from "@solidjs/router";
import { createContext, JSX, useContext } from "solid-js";

const clansContext = createContext<AccessorWithLatest<ClanList | undefined>>();

export function useClansContext() {
  return useContext(clansContext);
}

export function ClansContextProvider(props: {
  clans: AccessorWithLatest<ClanList | undefined>;
  children: JSX.Element;
}): JSX.Element {
  return (
    <clansContext.Provider value={props.clans}>
      {props.children}
    </clansContext.Provider>
  );
}
