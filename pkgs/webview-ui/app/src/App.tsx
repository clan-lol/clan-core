import { createSignal, type Component } from "solid-js";
import { CountProvider } from "./Config";
import { Layout } from "./layout/layout";
import { Route, Router } from "./Routes";

// Global state
const [route, setRoute] = createSignal<Route>("machines");

export { route, setRoute };

const App: Component = () => {
  return (
    <CountProvider>
      <Layout>
        <Router route={route} />
      </Layout>
    </CountProvider>
  );
};

export default App;
