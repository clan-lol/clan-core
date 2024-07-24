import { Accessor, For, Match, Switch } from "solid-js";
import { MachineListView } from "./routes/machines/view";
import { colors } from "./routes/colors/view";
import { CreateClan } from "./routes/clan/view";
import { HostList } from "./routes/hosts/view";
import { BlockDevicesView } from "./routes/blockdevices/view";
import { Flash } from "./routes/flash/view";
import { Settings } from "./routes/settings";
import { Welcome } from "./routes/welcome";
import { Deploy } from "./routes/deploy";
import { CreateMachine } from "./routes/machines/create";

export type Route = keyof typeof routes;

export const routes = {
  createClan: {
    child: CreateClan,
    label: "Create Clan",
    icon: "groups",
  },
  machines: {
    child: MachineListView,
    label: "Machines",
    icon: "devices_other",
  },
  "machines/add": {
    child: CreateMachine,
    label: "create Machine",
    icon: "add",
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
  settings: {
    child: Settings,
    label: "Settings",
    icon: "settings",
  },
  welcome: {
    child: Welcome,
    label: "welcome",
    icon: "settings",
  },
  deploy: {
    child: Deploy,
    label: "deploy",
    icon: "content_copy",
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
