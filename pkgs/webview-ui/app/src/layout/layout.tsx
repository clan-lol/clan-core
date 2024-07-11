import { Component, JSXElement, Show } from "solid-js";
import { Header } from "./header";
import { Sidebar } from "../Sidebar";
import { route, setRoute } from "../App";
import { effect } from "solid-js/web";

interface LayoutProps {
  children: JSXElement;
}

export const Layout: Component<LayoutProps> = (props) => {
  effect(() => {
    console.log(route());
  });
  return (
    <>
      <div class="drawer bg-base-100 lg:drawer-open">
        <input
          id="toplevel-drawer"
          type="checkbox"
          class="drawer-toggle hidden"
        />
        <div class="drawer-content">
          <Show when={route() !== "welcome"}>
            <Header />
          </Show>

          {props.children}
        </div>
        <div
          class="drawer-side z-40"
          classList={{ "!hidden": route() === "welcome" }}
        >
          <label
            for="toplevel-drawer"
            aria-label="close sidebar"
            class="drawer-overlay"
          ></label>
          <Sidebar route={route} setRoute={setRoute} />
        </div>
      </div>
    </>
  );
};
