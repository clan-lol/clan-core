import { Clan } from "@/src/models/Clan";
import { Accessor, createContext, JSX, useContext } from "solid-js";

const clanContext = createContext<Accessor<Clan>>();

export function useClanContext() {
  return useContext(clanContext);
}

export function ClanContextProvider(props: {
  clan: Accessor<Clan>;
  children: JSX.Element;
}): JSX.Element {
  return (
    <clanContext.Provider value={props.clan}>
      {props.children}
    </clanContext.Provider>
  );
}
