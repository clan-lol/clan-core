import { createContext, JSX, useContext } from "solid-js";
import { ClanList } from "./Clan";
import { AccessorWithLatest, createAsync } from "@solidjs/router";

export class ClanContext {
  readonly clans: AccessorWithLatest<ClanList | undefined>;

  constructor() {
    this.clans = createAsync(async () => await ClanList.get());
  }
}

const clanContext = createContext<ClanContext>();

export function useClanContext() {
  return useContext(clanContext);
}

export function ClanContextProvider(props: { children: JSX.Element }) {
  return (
    <clanContext.Provider value={new ClanContext()}>
      {props.children}
    </clanContext.Provider>
  );
}
