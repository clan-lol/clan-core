"use client";
import { DashboardCard } from "@/components/card";
import { Fab, Typography } from "@mui/material";
import { MouseEventHandler, ReactNode } from "react";

import AppsIcon from "@mui/icons-material/Apps";
import DevicesIcon from "@mui/icons-material/Devices";
import LanIcon from "@mui/icons-material/Lan";

type Action = {
  id: string;
  icon: ReactNode;
  label: ReactNode;
  eventHandler: MouseEventHandler<HTMLButtonElement>;
};

export const QuickActions = () => {
  const actions: Action[] = [
    {
      id: "network",
      icon: <LanIcon sx={{ mr: 1 }} />,
      label: "Network",
      eventHandler: (event) => {
        console.log({ event });
      },
    },
    {
      id: "apps",
      icon: <AppsIcon sx={{ mr: 1 }} />,
      label: "Apps",
      eventHandler: (event) => {
        console.log({ event });
      },
    },
    {
      id: "nodes",
      icon: <DevicesIcon sx={{ mr: 1 }} />,
      label: "Devices",
      eventHandler: (event) => {
        console.log({ event });
      },
    },
  ];
  return (
    <DashboardCard title="Quick Actions">
      <div className="flex h-full w-full items-center justify-start pb-10 align-bottom">
        <div className="flex w-full flex-col flex-wrap justify-evenly gap-2 sm:flex-row">
          {actions.map(({ id, icon, label, eventHandler }) => (
            <Fab
              className="w-fit self-center shadow-none"
              color="secondary"
              key={id}
              onClick={eventHandler}
              variant="extended"
            >
              {icon}
              <Typography>{label}</Typography>
            </Fab>
          ))}
        </div>
      </div>
    </DashboardCard>
  );
};
