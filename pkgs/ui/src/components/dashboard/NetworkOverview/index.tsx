import { DashboardCard } from "@/components/card";
import { NoDataOverlay } from "@/components/noDataOverlay";
import { status, Status, clanStatus } from "@/data/dashboardData";
import {
  Chip,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Typography,
} from "@mui/material";
import Link from "next/link";
import React from "react";

const statusColorMap: Record<
  Status,
  "default" | "primary" | "secondary" | "error" | "info" | "success" | "warning"
> = {
  online: "info",
  offline: "error",
  pending: "default",
};

const MAX_OTHERS = 5;

export const NetworkOverview = () => {
  const { self, other } = clanStatus;

  const firstOthers = other.slice(0, MAX_OTHERS);
  return (
    <DashboardCard title="Clan Overview">
      <List>
        <ListItem>
          <ListItemText primary={self.name} secondary={self.status} />
          <ListItemIcon>
            <Chip
              label={status[self.status]}
              color={statusColorMap[self.status]}
            />
          </ListItemIcon>
        </ListItem>
        <Divider flexItem />
        {!other.length && (
          <div className="my-3 flex h-full w-full justify-center align-middle">
            <NoDataOverlay
              label={
                <ListItemText
                  primary="No other nodes"
                  secondary={<Link href="/nodes">Add devices</Link>}
                />
              }
            />
          </div>
        )}
        {firstOthers.map((o) => (
          <ListItem key={o.id}>
            <ListItemText primary={o.name} secondary={o.status} />
            <ListItemIcon>
              <Chip label={status[o.status]} color={statusColorMap[o.status]} />
            </ListItemIcon>
          </ListItem>
        ))}
        {other.length > MAX_OTHERS && (
          <ListItem>
            <ListItemText
              secondary={` ${other.length - MAX_OTHERS} more ...`}
            />
          </ListItem>
        )}
      </List>
    </DashboardCard>
  );
};
