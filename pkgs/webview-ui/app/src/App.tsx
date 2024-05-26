import { Match, Switch, createSignal, type Component } from "solid-js";
import { CountProvider } from "./Config";
// import { Nested } from "./nested";
import { Layout } from "./layout/layout";
import cx from "classnames";
import { Nested } from "./nested";

type Route = "home" | "machines";

const App: Component = () => {
  const [route, setRoute] = createSignal<Route>("home");
  return (
    <CountProvider>
      <Layout>
        <div class="col-span-1">
          <div class={cx("text-zinc-500")}>Navigation</div>
          <ul>
            <li>
              <button
                onClick={() => setRoute("home")}
                classList={{ "bg-blue-500": route() === "home" }}
              >
                Home
              </button>
            </li>
            <li>
              {" "}
              <button
                onClick={() => setRoute("machines")}
                classList={{ "bg-blue-500": route() === "machines" }}
              >
                Machines
              </button>
            </li>
          </ul>
        </div>

        <div class="col-span-7">
          <div>{route()}</div>
          <Switch fallback={<p>{route()} not found</p>}>
            <Match when={route() == "home"}>
              <Nested />
            </Match>
            <Match when={route() == "machines"}>
              <div class="grid grid-cols-3 gap-2">
                <div class="h-10 w-20 bg-red-500">red</div>
                <div class="h-10 w-20 bg-green-500">green</div>
                <div class="h-10 w-20 bg-blue-500">blue</div>
                <div class="h-10 w-20 bg-yellow-500">yellow</div>
                <div class="h-10 w-20 bg-purple-500">purple</div>
                <div class="h-10 w-20 bg-cyan-500">cyan</div>
                <div class="h-10 w-20 bg-pink-500">pink</div>
              </div>
            </Match>
          </Switch>
        </div>
      </Layout>
    </CountProvider>
  );
};

export default App;
