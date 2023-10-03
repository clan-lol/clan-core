import { DashboardCard } from "@/components/card";
import { notificationData } from "@/data/dashboardData";
import {
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
} from "@mui/material";

import CheckIcon from "@mui/icons-material/Check";
import InfoIcon from "@mui/icons-material/Info";
import PriorityHighIcon from "@mui/icons-material/PriorityHigh";
import CloseIcon from "@mui/icons-material/Close";

const severityMap = {
  info: {
    icon: <InfoIcon />,
    color: "info",
  },
  success: {
    icon: <CheckIcon />,
    color: "success",
  },
  warning: {
    icon: <PriorityHighIcon />,
    color: "warning",
  },
  error: {
    icon: <CloseIcon />,
    color: "error",
  },
};

export const Notifications = () => {
  return (
    <DashboardCard title="Notifications">
      <List>
        {notificationData.map((n, idx) => (
          <ListItem key={idx}>
            <ListItemAvatar>
              <Avatar
                sx={{
                  bgcolor: `${n.severity}.main`,
                }}
              >
                {severityMap[n.severity].icon}
              </Avatar>
            </ListItemAvatar>
            <ListItemText
              primary={n.msg}
              secondary={n.date}
              sx={{
                width: "100px",
              }}
            />
            <ListItemText
              primary={n.source}
              sx={{
                width: "100px",
              }}
            />
          </ListItem>
        ))}
      </List>
    </DashboardCard>
  );
};
