import type { Meta, StoryObj } from "@kachurun/storybook-solid";
import {
  createMemoryHistory,
  MemoryRouter,
  Route,
  RouteSectionProps,
} from "@solidjs/router";
import {
  SidebarNav,
  SidebarNavProps,
} from "@/src/components/Sidebar/SidebarNav";
import { Suspense } from "solid-js";
import { StoryContext } from "@kachurun/storybook-solid-vite";

const sidebarNavProps: SidebarNavProps = {
  clanLinks: [
    { label: "Brian's Clan", path: "/clans/1" },
    { label: "Dave's Clan", path: "/clans/2" },
    { label: "Mic92's Clan", path: "/clans/3" },
  ],
  clanDetail: {
    label: "Brian's Clan",
    settingsPath: "/clans/1/settings",
    machines: [
      {
        label: "Backup & Home",
        path: "/clans/1/machine/backup",
        serviceCount: 3,
        status: "Online",
      },
      {
        label: "Raspberry Pi",
        path: "/clans/1/machine/pi",
        serviceCount: 1,
        status: "Offline",
      },
      {
        label: "Mom's Laptop",
        path: "/clans/1/machine/moms-laptop",
        serviceCount: 2,
        status: "Installed",
      },
      {
        label: "Dad's Laptop",
        path: "/clans/1/machine/dads-laptop",
        serviceCount: 4,
        status: "Not Installed",
      },
    ],
  },
  extraSections: [
    {
      label: "Tools",
      links: [
        { label: "Borgbackup", path: "/clans/1/service/borgbackup" },
        { label: "Syncthing", path: "/clans/1/service/syncthing" },
        { label: "Mumble", path: "/clans/1/service/mumble" },
        { label: "Minecraft", path: "/clans/1/service/minecraft" },
      ],
    },
    {
      label: "Links",
      links: [
        { label: "GitHub", path: "https://github.com/brian-the-dev" },
        { label: "Twitter", path: "https://twitter.com/brian_the_dev" },
        {
          label: "LinkedIn",
          path: "https://www.linkedin.com/in/brian-the-dev/",
        },
        {
          label: "Instagram",
          path: "https://www.instagram.com/brian_the_dev/",
        },
      ],
    },
  ],
};

const meta: Meta<RouteSectionProps> = {
  title: "Components/Sidebar/Nav",
  component: SidebarNav,
  render: (_: never, context: StoryContext<SidebarNavProps>) => {
    const history = createMemoryHistory();
    history.set({ value: "/clans/1/machine/backup" });

    return (
      <div style="height: 670px;">
        <MemoryRouter
          history={history}
          root={(props) => (
            <Suspense>
              <SidebarNav {...sidebarNavProps} />
            </Suspense>
          )}
        >
          <Route path="/clans/1/machine/backup" component={(props) => <></>} />
        </MemoryRouter>
      </div>
    );
  },
};

export default meta;

type Story = StoryObj<RouteSectionProps>;

export const Default: Story = {
  args: {},
};
