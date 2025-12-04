import { Clan, Clans, ClanSetters, ClansSetters } from "@/src/models";
import { Accessor, createContext, JSX, useContext } from "solid-js";

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

export function ClansContextProvider(props: {
  value: [Clans, ClansSetters];
  children: JSX.Element;
}): JSX.Element {
  return (
    <ClansContext.Provider value={props.value}>
      {props.children}
    </ClansContext.Provider>
  );
}

const ClanContext = createContext<[Accessor<Clan>, ClanSetters]>();

export function useClanContext(): [Accessor<Clan>, ClanSetters] {
  const value = useContext(ClanContext);
  if (!value) {
    throw new Error("useClanContext must be used within a ClanContextProvider");
  }
  return value;
}

export function ClanContextProvider(props: {
  value: [Accessor<Clan>, ClanSetters];
  children: JSX.Element;
}): JSX.Element {
  return (
    <ClanContext.Provider value={props.value}>
      {props.children}
    </ClanContext.Provider>
  );
}
