import {
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import Image from "next/image";
import { ReactNode } from "react";

import { tw } from "@/utils/tailwind";
import AppsIcon from "@mui/icons-material/Apps";
import BackupIcon from "@mui/icons-material/Backup";
import DashboardIcon from "@mui/icons-material/Dashboard";
import DesignServicesIcon from "@mui/icons-material/DesignServices";
import DevicesIcon from "@mui/icons-material/Devices";
import LanIcon from "@mui/icons-material/Lan";
import Link from "next/link";

import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";

type MenuEntry = {
  icon: ReactNode;
  label: string;
  to: string;
  disabled: boolean;
} & {
  subMenuEntries?: MenuEntry[];
};

const menuEntries: MenuEntry[] = [
  {
    icon: <DashboardIcon />,
    label: "Dashoard",
    to: "/",
    disabled: false,
  },
  {
    icon: <DevicesIcon />,
    label: "Machines",
    to: "/machines",
    disabled: false,
  },
  {
    icon: <AppsIcon />,
    label: "Applications",
    to: "/applications",
    disabled: true,
  },
  {
    icon: <LanIcon />,
    label: "Network",
    to: "/network",
    disabled: true,
  },
  {
    icon: <DesignServicesIcon />,
    label: "Templates",
    to: "/templates",
    disabled: false,
  },
  {
    icon: <BackupIcon />,
    label: "Backups",
    to: "/backups",
    disabled: true,
  },
];

const hideSidebar = tw`-translate-x-14 lg:-translate-x-64`;
const showSidebar = tw`lg:translate-x-0`;

interface SidebarProps {
  show: boolean;
  onClose: () => void;
  clanSelect: React.ReactNode;
}
export function Sidebar(props: SidebarProps) {
  const { show, onClose, clanSelect } = props;

  return (
    <aside
      className={tw`${
        show ? showSidebar : hideSidebar
      } z-9999 static left-0  top-0 flex h-screen w-14 flex-col overflow-x-hidden overflow-y-hidden bg-neutral-10 transition duration-150 ease-in-out dark:bg-neutral-2 lg:w-64`}
    >
      <div className="flex items-center justify-between gap-2 overflow-hidden px-0 py-5 lg:p-6">
        <div className="mt-8 hidden w-full text-center font-semibold text-white lg:block">
          <Image
            src="/logo.png"
            alt="Clan Logo"
            width={75}
            height={75}
            priority
          />
        </div>
      </div>
      <div className="self-center">{clanSelect}</div>
      <Divider
        flexItem
        className="mx-8 mb-4 mt-9 hidden bg-neutral-40 lg:block"
      />
      <div className="flex w-full justify-center">
        <IconButton size="large" className="text-white" onClick={onClose}>
          <ChevronLeftIcon fontSize="inherit" />
        </IconButton>
      </div>
      <div className="flex flex-col overflow-hidden overflow-y-auto">
        <List className="mb-14 px-0 pb-4 text-white lg:mt-1 lg:px-4">
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
                  disabled={menuEntry.disabled}
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
        <Divider
          flexItem
          className="mx-8 my-10 hidden bg-neutral-40 lg:block"
        />
        <div className="mx-auto mb-8 hidden w-full max-w-xs rounded-sm px-4 py-6 text-center align-bottom shadow-sm lg:block">
          <h3 className="mb-2 w-full font-semibold text-white">
            Clan.lol Admin
          </h3>
          <a
            href=""
            target="_blank"
            rel="nofollow"
            className="inline-block w-full rounded-md p-2 text-center text-white hover:text-purple-60/95"
          >
            Donate
          </a>
        </div>
      </div>
    </aside>
  );
}
