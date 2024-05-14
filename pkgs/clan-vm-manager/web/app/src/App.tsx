import { Match, Switch, createSignal, type Component } from "solid-js";
import { CountProvider } from "./Config";
import { Nested } from "./nested";

type Route = "home" | "graph";

const App: Component = () => {
  const [route, setRoute] = createSignal<Route>("home");
  return (
    <CountProvider>
      <div class="w-full flex items-center flex-col gap-2 my-2">
        <div>Clan</div>

        <div class="flex items-center">
          <button
            onClick={() => setRoute((o) => (o === "graph" ? "home" : "graph"))}
            class="btn btn-link"
          >
            Navigate to {route() === "home" ? "graph" : "home"}
          </button>
          <Switch fallback={<p>{route()} not found</p>}>
            <Match when={route() == "home"}>
              <p>Current route: {route()}</p>
            </Match>
            <Match when={route() == "graph"}>
              <p>Current route: {route()}</p>
            </Match>
          </Switch>
        </div>
        <div class="flex items-center">
          <Nested />
        </div>
      </div>
    </CountProvider>
  );
};

export default App;
