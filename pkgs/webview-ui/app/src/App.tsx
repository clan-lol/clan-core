import { createEffect, createSignal, type Component } from "solid-js";
import { Layout } from "./layout/layout";
import { Route, Router } from "./Routes";
import { Toaster } from "solid-toast";
import { effect } from "solid-js/web";
import { makePersisted } from "@solid-primitives/storage";

// Some global state
const [route, setRoute] = createSignal<Route>("machines");
createEffect(() => {
  console.log(route());
});

export { route, setRoute };

const [activeURI, setActiveURI] = makePersisted(
  createSignal<string | null>(null),
  {
    name: "activeURI",
    storage: localStorage,
  }
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
  return [
    <Toaster position="top-right" />,
    <Layout>
      <Router route={route} />
    </Layout>,
  ];
};

export default App;
