import { Typography } from "@mui/material";
import { ReactNode } from "react";

interface DashboardCardProps {
  title: ReactNode;
  children?: ReactNode;
}
const DashboardCard = (props: DashboardCardProps) => {
  const { children, title } = props;
  return (
    <div className="h-full w-full bg-white dark:bg-neutral-5">
      <div className="h-full w-full px-3 py-2">
        <Typography variant="h6" color={"primary"}>
          {title}
        </Typography>
        {children}
      </div>
    </div>
  );
};

export { DashboardCard };
