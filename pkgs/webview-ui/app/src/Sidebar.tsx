import { Accessor, For, Setter } from "solid-js";
import { Route, routes } from "./Routes";
import { activeURI } from "./App";
import { createQuery } from "@tanstack/solid-query";
import { callApi } from "./api";

interface SidebarProps {
  route: Accessor<Route>;
  setRoute: Setter<Route>;
}
export const Sidebar = (props: SidebarProps) => {
  const query = createQuery(() => ({
    queryKey: [activeURI(), "meta"],
    queryFn: async () => {
      const curr = activeURI();
      if (curr) {
        const result = await callApi("show_clan_meta", { uri: curr });
        if (result.status === "error") throw new Error("Failed to fetch data");
        return result.data;
      }
    },
  }));
  const { route, setRoute } = props;
  return (
    <aside class="w-80 rounded-xl border border-slate-900 bg-slate-800  pb-10">
      <div class="m-4 flex flex-col text-center capitalize text-white">
        <span class="text-lg">{query.data?.name}</span>
        <span class="text-sm">{query.data?.description}</span>
      </div>
      <ul class="menu px-4 py-0">
        <For each={Object.entries(routes)}>
          {([key, { label, icon }]) => (
            <li>
              <button
                onClick={() => setRoute(key as Route)}
                class="group text-white"
                classList={{ "!bg-primary !text-white": route() === key }}
              >
                <span class="material-icons">{icon}</span>
                {label}
              </button>
            </li>
          )}
        </For>
      </ul>
    </aside>
  );
};
