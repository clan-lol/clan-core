import { Accessor, For, Setter } from "solid-js";
import { Route, routes } from "./Routes";

interface SidebarProps {
  route: Accessor<Route>;
  setRoute: Setter<Route>;
}
export const Sidebar = (props: SidebarProps) => {
  const { route, setRoute } = props;
  return (
    <aside class="min-h-screen w-80 bg-base-100">
      <div class="sticky top-0 z-20 items-center gap-2 bg-base-100/90 px-4 py-2 shadow-sm backdrop-blur lg:flex">
        Icon
      </div>
      <ul class="menu px-4 py-0">
        <For each={Object.entries(routes)}>
          {([key, { label, icon }]) => (
            <li>
              <button
                onClick={() => setRoute(key as Route)}
                class="group"
                classList={{ "bg-blue-500": route() === key }}
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
