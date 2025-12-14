import { Accessor, createContext, FlowComponent, useContext } from "solid-js";
import { Clan, ClanMethods, ClansEntity, Clans, ClansMethods } from "..";
import { createClansStore } from "./clans";
import { createClanStore } from "./clan";

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
  value: Accessor<ClansEntity>;
}> = (props) => {
  return (
    <ClansContext.Provider value={createClansStore(props.value)}>
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
  value: Accessor<Clan>;
}> = (props) => {
  return (
    <ClanContext.Provider value={createClanStore(props.value)}>
      {props.children}
    </ClanContext.Provider>
  );
};
