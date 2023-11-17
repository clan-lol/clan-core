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
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import DashboardIcon from "@mui/icons-material/Dashboard";
import DevicesIcon from "@mui/icons-material/Devices";
import Link from "next/link";

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
    icon: <BackupIcon />,
    label: "Backups",
    to: "/backups",
    disabled: true,
  },
  // {
  //   icon: <LanIcon />,
  //   label: "Network",
  //   to: "/network",
  //   disabled: true,
  // },
  // {
  //   icon: <DesignServicesIcon />,
  //   label: "Templates",
  //   to: "/templates",
  //   disabled: false,
  // },
];

const hideSidebar = tw`-translate-x-14 lg:-translate-x-64`;
const showSidebar = tw`lg:translate-x-0`;

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
      } z-9999 static left-0  top-0 flex h-screen w-14 flex-col overflow-x-hidden overflow-y-hidden bg-blue-3 transition duration-150 ease-in-out lg:w-64`}
    >
      <div className="mt-8 flex flex-col py-6">
        <div className="hidden w-full max-w-xs text-center shadow-sm lg:block">
          <h3 className="m-0 w-full pb-2 font-semibold text-white">
            Clan Dashboard
          </h3>
        </div>
        <div className="flex items-center overflow-hidden">
          <div className="hidden w-full text-center font-semibold text-white lg:block">
            <Image
              src="/clan-white.png"
              alt="Clan Logo"
              width={102}
              height={75}
              priority
            />
          </div>
        </div>
      </div>
      <Divider flexItem className="mx-8 my-4 hidden bg-blue-40 lg:block" />
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
        <Divider flexItem className="mx-8 my-4 hidden bg-blue-40 lg:block" />
        <div className="flex w-full justify-center py-2">
          <IconButton size="large" className="text-white" onClick={onClose}>
            <ChevronLeftIcon fontSize="inherit" />
          </IconButton>
        </div>
      </div>
    </aside>
  );
}
