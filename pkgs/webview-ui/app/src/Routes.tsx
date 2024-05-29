import { Accessor, For, Match, Switch } from "solid-js";
import { MachineListView } from "./routes/machines/view";
import { colors } from "./routes/colors/view";

export type Route = keyof typeof routes;

export const routes = {
  machines: {
    child: MachineListView,
    label: "Machines",
    icon: "devices_other",
  },
  colors: {
    child: colors,
    label: "Colors",
    icon: "color_lens",
  },
};

interface RouterProps {
  route: Accessor<Route>;
}
export const Router = (props: RouterProps) => {
  const { route } = props;
  return (
    <Switch fallback={<p>route {route()} not found</p>}>
      <For each={Object.entries(routes)}>
        {([key, { child }]) => <Match when={route() === key}>{child}</Match>}
      </For>
    </Switch>
  );
};
