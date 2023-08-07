import {
  Divider,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import Image from "next/image";
import { ReactNode } from "react";

import DashboardIcon from "@mui/icons-material/Dashboard";
import DevicesIcon from "@mui/icons-material/Devices";
import LanIcon from "@mui/icons-material/Lan";
import AppsIcon from "@mui/icons-material/Apps";
import DesignServicesIcon from "@mui/icons-material/DesignServices";
import BackupIcon from "@mui/icons-material/Backup";
import Link from "next/link";

type MenuEntry = {
  icon: ReactNode;
  label: string;
  to: string;
} & {
  subMenuEntries?: MenuEntry[];
};

const menuEntries: MenuEntry[] = [
  {
    icon: <DashboardIcon />,
    label: "Dashoard",
    to: "/",
  },
  {
    icon: <DevicesIcon />,
    label: "Devices",
    to: "/nodes",
  },
  {
    icon: <AppsIcon />,
    label: "Applications",
    to: "/applications",
  },
  {
    icon: <LanIcon />,
    label: "Network",
    to: "/network",
  },
  {
    icon: <DesignServicesIcon />,
    label: "Templates",
    to: "/templates",
  },
  {
    icon: <BackupIcon />,
    label: "Backups",
    to: "/backups",
  },
];

export function Sidebar() {
  return (
    <aside className="absolute left-0 top-0 z-9999 flex h-screen w-12 sm:w-64 flex-col overflow-y-hidden  bg-zinc-950 dark:bg-boxdark sm:static">
      <div className="flex items-center justify-between gap-2 px-6 py-5.5 lg:py-6.5">
        <div className="mt-8 font-semibold text-white w-full text-center hidden sm:block">
          <Image
            src="/logo.svg"
            alt="Clan Logo"
            width={58}
            height={58}
            priority
          />
        </div>
      </div>
      <Divider flexItem className="bg-zinc-600 my-9 mx-8" />
      <div className="overflow-hidden flex flex-col overflow-y-auto duration-200 ease-linear">
        <List className="pb-4 mb-14 px-4 lg:mt-1 lg:px-6 text-white">
          {menuEntries.map((menuEntry, idx) => {
            return (
              <ListItem key={idx}>
                <ListItemButton
                  className="justify-center sm:justify-normal"
                  LinkComponent={Link}
                  href={menuEntry.to}
                >
                  <ListItemIcon
                    color="inherit"
                    className="justify-center sm:justify-normal text-white"
                  >
                    {menuEntry.icon}
                  </ListItemIcon>
                  <ListItemText
                    primary={menuEntry.label}
                    primaryTypographyProps={{
                      color: "inherit",
                    }}
                    className="hidden sm:block"
                  />
                </ListItemButton>
              </ListItem>
            );
          })}
        </List>
        <Divider flexItem className="bg-zinc-600 mx-8 my-10" />
        <div className="hidden sm:block mx-auto mb-8 w-full max-w-60 rounded-sm py-6 px-4 text-center shadow-default align-bottom">
          <h3 className="mb-1 w-full font-semibold text-white">
            Clan.lol Admin
          </h3>

          <a
            href=""
            target="_blank"
            rel="nofollow"
            className="w-full text-center rounded-md bg-primary p-2 text-white hover:bg-opacity-95"
          >
            Donate
          </a>
        </div>
      </div>
    </aside>
  );
}
