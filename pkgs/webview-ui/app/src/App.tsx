import { createSignal } from "solid-js";
import { makePersisted } from "@solid-primitives/storage";
import { callApi } from "./api";

const [activeURI, setActiveURI] = makePersisted(
  createSignal<string | null>(null),
  {
    name: "activeURI",
    storage: localStorage,
  },
);

export { activeURI, setActiveURI };

const [clanList, setClanList] = makePersisted(createSignal<string[]>([]), {
  name: "clanList",
  storage: localStorage,
});

export { clanList, setClanList };

(async function () {
  const curr = activeURI();
  if (curr) {
    const result = await callApi("show_clan_meta", { uri: curr });
    console.log("refetched meta for ", curr);
    if (result.status === "error") {
      result.errors.forEach((error) => {
        if (error.description === "clan directory does not exist") {
          setActiveURI(null);
          setClanList((clans) => clans.filter((clan) => clan !== curr));
        }
      });
    }
  }
})();

// ensure to null out activeURI on startup if the clan was deleted
// => throws user back to the view for selecting a clan
