import { Component, createEffect, Show } from "solid-js";
import { Header } from "./header";
import { Sidebar } from "../Sidebar";
import { activeURI, clanList } from "../App";
import { RouteSectionProps } from "@solidjs/router";

export const Layout: Component<RouteSectionProps> = (props) => {
  return (
    <div class="h-screen bg-gradient-to-b from-white to-base-100 p-4">
      <div class="drawer lg:drawer-open ">
        <input
          id="toplevel-drawer"
          type="checkbox"
          class="drawer-toggle hidden"
        />
        <div class="drawer-content">
          <Show when={props.location.pathname !== "welcome"}>
            <Header clan_dir={activeURI} />
          </Show>
          {props.children}
        </div>
        <div
          class="drawer-side z-40 h-full"
          classList={{
            "!hidden":
              props.location.pathname === "welcome" || clanList().length === 0,
          }}
        >
          <label
            for="toplevel-drawer"
            aria-label="close sidebar"
            class="drawer-overlay"
          ></label>
          <Sidebar {...props} />
        </div>
      </div>
    </div>
  );
};
