import { type Component, createEffect, createSignal } from "solid-js";
import { Layout } from "./layout/layout";
import { Route, Router } from "./Routes";
import { Toaster } from "solid-toast";
import { effect } from "solid-js/web";
import { makePersisted } from "@solid-primitives/storage";

// Some global state
const [route, setRoute] = createSignal<Route>("machines");

export { route, setRoute };

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

const App: Component = () => {
  effect(() => {
    if (clanList().length === 0) {
      setRoute("welcome");
    }
  });
  return (
    <div class="h-screen bg-gradient-to-b from-white to-base-100 p-4">
      <Toaster position="top-right" />
      <Layout>
        <Router route={route} />
      </Layout>
    </div>
  );
};

export default App;
