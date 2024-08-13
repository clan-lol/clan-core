import { Component, JSXElement, Show } from "solid-js";
import { Header } from "./header";
import { Sidebar } from "../Sidebar";
import { activeURI, clanList, route, setRoute } from "../App";

interface LayoutProps {
  children: JSXElement;
}

export const Layout: Component<LayoutProps> = (props) => {
  return (
    <>
      <div class="drawer lg:drawer-open ">
        <input
          id="toplevel-drawer"
          type="checkbox"
          class="drawer-toggle hidden"
        />
        <div class="drawer-content">
          <Show when={route() !== "welcome"}>
            <Header clan_dir={activeURI} />
          </Show>
          {props.children}
        </div>
        <div
          class="drawer-side z-40 h-full"
          classList={{
            "!hidden": route() === "welcome" || clanList().length === 0,
          }}
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
