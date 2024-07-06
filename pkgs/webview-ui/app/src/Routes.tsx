import { Accessor, For, Match, Switch } from "solid-js";
import { MachineListView } from "./routes/machines/view";
import { colors } from "./routes/colors/view";
import { clan } from "./routes/clan/view";
import { HostList } from "./routes/hosts/view";
import { BlockDevicesView } from "./routes/blockdevices/view";
import { Flash } from "./routes/flash/view";

export type Route = keyof typeof routes;

export const routes = {
  clan: {
    child: clan,
    label: "Clan",
    icon: "groups",
  },
  machines: {
    child: MachineListView,
    label: "Machines",
    icon: "devices_other",
  },
  hosts: {
    child: HostList,
    label: "hosts",
    icon: "devices_other",
  },
  flash: {
    child: Flash,
    label: "create_flash_installer",
    icon: "devices_other",
  },
  blockdevices: {
    child: BlockDevicesView,
    label: "blockdevices",
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
