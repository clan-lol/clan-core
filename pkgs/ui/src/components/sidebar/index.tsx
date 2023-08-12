import {
  Divider,
  Icon,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import Image from "next/image";
import { ReactNode, useState } from "react";

import DashboardIcon from "@mui/icons-material/Dashboard";
import DevicesIcon from "@mui/icons-material/Devices";
import LanIcon from "@mui/icons-material/Lan";
import AppsIcon from "@mui/icons-material/Apps";
import DesignServicesIcon from "@mui/icons-material/DesignServices";
import BackupIcon from "@mui/icons-material/Backup";
import Link from "next/link";
import { tw } from "@/utils/tailwind";

import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";

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

const hideSidebar = tw`-translate-x-12 absolute lg:-translate-x-64`;
const showSidebar = tw`lg:translate-x-0 static`;

interface SidebarProps {
  show: boolean;
  onClose: () => void;
}
export function Sidebar(props: SidebarProps) {
  const { show, onClose } = props;
  return (
    <aside
      className={tw`${
        show ? showSidebar : hideSidebar
      } z-9999 dark:bg-boxdark left-0 top-0 flex h-screen w-12 flex-col overflow-x-hidden overflow-y-hidden bg-zinc-950 lg:w-64 transition ease-in-out duration-150`}
    >
      <div className="py-5.5 lg:py-6.5 flex items-center justify-between gap-2 overflow-hidden px-0 lg:px-6">
        <div className="mt-8 hidden w-full text-center font-semibold text-white lg:block">
          <Image
            src="/logo.svg"
            alt="Clan Logo"
            width={58}
            height={58}
            priority
          />
        </div>
      </div>
      <Divider
        flexItem
        className="mx-8 mb-4 mt-9 bg-zinc-600 hidden lg:block"
      />
      <div className="w-full flex justify-center">
        <IconButton size="large" className="text-white" onClick={onClose}>
          <ChevronLeftIcon fontSize="inherit" />
        </IconButton>
      </div>
      <div className="flex flex-col overflow-hidden overflow-y-auto">
        <List className="mb-14 px-0 pb-4 text-white lg:px-4 lg:mt-1">
          {menuEntries.map((menuEntry, idx) => {
            return (
              <ListItem
                key={idx}
                disablePadding
                className="!overflow-hidden py-2"
              >
                <ListItemButton
                  className="justify-center lg:justify-normal"
                  LinkComponent={Link}
                  href={menuEntry.to}
                >
                  <ListItemIcon
                    color="inherit"
                    className="justify-center overflow-hidden text-white lg:justify-normal"
                  >
                    {menuEntry.icon}
                  </ListItemIcon>
                  <ListItemText
                    primary={menuEntry.label}
                    primaryTypographyProps={{
                      color: "inherit",
                    }}
                    className="hidden lg:block"
                  />
                </ListItemButton>
              </ListItem>
            );
          })}
        </List>

        <Divider flexItem className="mx-8 my-10 bg-zinc-600 hidden lg:block" />
        <div className="max-w-60 shadow-default mx-auto mb-8 hidden w-full rounded-sm px-4 py-6 text-center align-bottom lg:block">
          <h3 className="mb-1 w-full font-semibold text-white">
            Clan.lol Admin
          </h3>
          <a
            href=""
            target="_blank"
            rel="nofollow"
            className="bg-primary w-full rounded-md p-2 text-center text-white hover:bg-opacity-95"
          >
            Donate
          </a>
        </div>
      </div>
    </aside>
  );
}
