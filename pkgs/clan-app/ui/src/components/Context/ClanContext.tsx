import {
  Clan,
  Clans,
  ClansEntity,
  ClanSetters,
  ClansSetters,
  createClansStore,
  createClanStore,
} from "@/src/models";
import { Accessor, Component, createContext, JSX, useContext } from "solid-js";

const ClansContext = createContext<[Clans, ClansSetters]>();

export function useClansContext(): [Clans, ClansSetters] {
  const value = useContext(ClansContext);
  if (!value) {
    throw new Error(
      "useClansContext must be used within a ClansContextProvider",
    );
  }
  return value;
}

export const ClansContextProvider: Component<{
  clans: Accessor<ClansEntity>;
  children: JSX.Element;
}> = (props) => {
  return (
    <ClansContext.Provider value={createClansStore(props.clans)}>
      {props.children}
    </ClansContext.Provider>
  );
};

const ClanContext = createContext<[Accessor<Clan>, ClanSetters]>();

export function useClanContext(): [Accessor<Clan>, ClanSetters] {
  const value = useContext(ClanContext);
  if (!value) {
    throw new Error("useClanContext must be used within a ClanContextProvider");
  }
  return value;
}

export const ClanContextProvider: Component<{
  clan: Accessor<Clan>;
  children: JSX.Element;
}> = (props) => {
  const value = useClansContext();
  return (
    <ClanContext.Provider value={createClanStore(props.clan, value)}>
      {props.children}
    </ClanContext.Provider>
  );
};
