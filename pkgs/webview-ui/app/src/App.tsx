import { createSignal, type Component } from "solid-js";
import { MachineProvider } from "./Config";
import { Layout } from "./layout/layout";
import { Route, Router } from "./Routes";

// Global state
const [route, setRoute] = createSignal<Route>("machines");

export { route, setRoute };

const App: Component = () => {
  return (
    <MachineProvider>
      <Layout>
        <Router route={route} />
      </Layout>
    </MachineProvider>
  );
};

export default App;
