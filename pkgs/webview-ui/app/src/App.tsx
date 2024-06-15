import { createSignal, type Component } from "solid-js";
import { MachineProvider } from "./Config";
import { Layout } from "./layout/layout";
import { Route, Router } from "./Routes";
import { Toaster } from "solid-toast";

// Global state
const [route, setRoute] = createSignal<Route>("machines");

const [currClanURI, setCurrClanURI] = createSignal<string>(
  "/home/johannes/1_clans/myclan"
);

export { currClanURI, setCurrClanURI };

export { route, setRoute };

const App: Component = () => {
  return [
    <Toaster position="top-right" />,
    <MachineProvider>
      <Layout>
        <Router route={route} />
      </Layout>
    </MachineProvider>,
  ];
};

export default App;
