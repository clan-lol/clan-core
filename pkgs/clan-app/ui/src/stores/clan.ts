import { createStore, produce } from "solid-js/store";
import { makePersisted } from "@solid-primitives/storage";

export type SceneData = Record<string, { position: [number, number] }>;

interface ClanStoreType {
  clanURIs: string[];
  activeClanURI?: string;
  sceneData: Record<string, SceneData>;
  queryCache: {
    clanDetails: Record<string, string>;
  };
}

const [store, setStore] = makePersisted(
  createStore<ClanStoreType>({
    clanURIs: [],
    sceneData: {},
    queryCache: {
      clanDetails: {},
    },
  }),
  {
    name: "clanStore",
    storage: localStorage,
  },
);

const resetStore = () => {
  setStore({
    clanURIs: [],
    activeClanURI: undefined,
    sceneData: {},
  });
};

/**
 * Retrieves the active clan URI from the store.
 *
 * @function
 * @returns {string} The URI of the active clan.
 */
const activeClanURI = () => store.activeClanURI;

/**
 * Updates the active Clan URI in the store.
 *
 * @param {string} uri - The URI to be set as the active Clan URI.
 */
const setActiveClanURI = (uri: string | undefined) =>
  setStore("activeClanURI", uri);

/**
 * Retrieves the current list of clan URIs from the store.
 *
 * @function clanURIs
 * @returns {*} The clan URIs from the store.
 */
const clanURIs = (): string[] => store.clanURIs;

/**
 * Adds a new clan URI to the list of clan URIs in the store.
 *
 * @param {string} uri - The URI of the clan to be added.
 *
 */
const addClanURI = (uri: string) => {
  setStore(
    produce((state) => {
      // check if it's already in the list
      if (state.clanURIs.find((clanURI) => clanURI == uri)) {
        return;
      }

      // otherwise add it
      state.clanURIs = [...state.clanURIs, uri];

      // initiliase empty scene data
      state.sceneData[uri] = {};
    }),
  );
};

/**
 * Removes a specified URI from the clan URI list and updates the active clan URI.
 *
 * This function modifies the store in the following ways:
 * - Removes the specified URI from the `clanURIs` array.
 * - Clears the `activeClanURI` if the removed URI matches the currently active URI.
 * - Sets a new active clan URI to the last URI in the `clanURIs` array if the active clan URI is undefined
 *   and there are remaining clan URIs in the list.
 *
 * @param {string} uri - The URI to be removed from the clan list.
 */
const removeClanURI = (uri: string) => {
  setStore(
    produce((state) => {
      // remove from the clan list
      state.clanURIs = state.clanURIs.filter((el) => el !== uri);

      // clear active clan uri if it's the one being removed
      if (state.activeClanURI === uri) {
        state.activeClanURI = undefined;
      }

      // select a new active URI if at least one remains
      if (!state.activeClanURI && state.clanURIs.length > 0) {
        state.activeClanURI = state.clanURIs[state.clanURIs.length - 1];
      }
    }),
  );
};

export {
  store,
  setStore,
  activeClanURI,
  setActiveClanURI,
  clanURIs,
  addClanURI,
  removeClanURI,
  resetStore,
};
