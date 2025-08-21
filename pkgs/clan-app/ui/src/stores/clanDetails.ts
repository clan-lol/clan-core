import { produce } from "solid-js/store";
import { AsyncStorage } from "@tanstack/query-persist-client-core";
import { setStore, store } from "@/src/stores/clan";

class ClanDetailsStoreImpl implements AsyncStorage {
  entries() {
    return Object.entries(store.queryCache.clanDetails);
  }

  getItem(key: string) {
    return store.queryCache.clanDetails[key];
  }

  removeItem(key: string) {
    setStore(
      produce((state) => {
        // eslint-disable-next-line @typescript-eslint/no-dynamic-delete
        delete state.queryCache.clanDetails[key];
      }),
    );
  }

  setItem(key: string, value: string) {
    return setStore(
      produce((state) => {
        state.queryCache.clanDetails[key] = value;
      }),
    );
  }
}

export const ClanDetailsStore = new ClanDetailsStoreImpl();
