import { Accessor, createContext, FlowComponent, useContext } from "solid-js";
import { Clan, ClanMethods, ClansEntity, Clans, ClansMethods } from "..";
import { createClanStore } from "./clan";
import { createClansStore } from "./clans";

const ClansContext = createContext<readonly [Clans, ClansMethods]>();

export function useClansContext(): readonly [Clans, ClansMethods] {
  const value = useContext(ClansContext);
  if (!value) {
    throw new Error(
      "useClansContext must be used within a ClansContextProvider",
    );
  }
  return value;
}

export const ClansContextProvider: FlowComponent<{
  clans: Accessor<ClansEntity>;
}> = (props) => {
  return (
    <ClansContext.Provider value={createClansStore(props.clans)}>
      {props.children}
    </ClansContext.Provider>
  );
};

const ClanContext = createContext<readonly [Accessor<Clan>, ClanMethods]>();

export function useClanContext(): readonly [Accessor<Clan>, ClanMethods] {
  const value = useContext(ClanContext);
  if (!value) {
    throw new Error("useClanContext must be used within a ClanContextProvider");
  }
  return value;
}

export const ClanContextProvider: FlowComponent<{
  clan: Accessor<Clan>;
}> = (props) => {
  const value = useClansContext();
  return (
    <ClanContext.Provider value={createClanStore(props.clan, value)}>
      {props.children}
    </ClanContext.Provider>
  );
};
