import { createContext, createEffect, JSX, useContext } from "solid-js";
import { callApi } from "@/src/api";
import {
  activeClanURI,
  addClanURI,
  clanURIs,
  removeClanURI,
  setActiveClanURI,
  store,
} from "@/src/stores/clan";
import { redirect } from "@solidjs/router";

// Create the context
interface ClanContextType {
  activeClanURI: typeof activeClanURI;
  setActiveClanURI: typeof setActiveClanURI;
  clanURIs: typeof clanURIs;
  addClanURI: typeof addClanURI;
  removeClanURI: typeof removeClanURI;
}

const ClanContext = createContext<ClanContextType>({
  activeClanURI,
  setActiveClanURI,
  clanURIs,
  addClanURI,
  removeClanURI,
});

interface ClanProviderProps {
  children: JSX.Element;
}

export function ClanProvider(props: ClanProviderProps) {
  // redirect to welcome if there's no active clan and no clan URIs
  createEffect(async () => {
    if (!store.activeClanURI && store.clanURIs.length == 0) {
      redirect("/welcome");
      return;
    }
  });

  return (
    <ClanContext.Provider
      value={{
        activeClanURI,
        setActiveClanURI,
        clanURIs,
        addClanURI,
        removeClanURI,
      }}
    >
      {props.children}
    </ClanContext.Provider>
  );
}

// Export a hook that provides access to the context
export function useClanContext() {
  const context = useContext(ClanContext);
  if (!context) {
    throw new Error("useClanContext must be used within a ClanProvider");
  }
  return context;
}
