import { Typography } from "@mui/material";
import { ReactNode } from "react";

interface DashboardCardProps {
  title: ReactNode;
  children?: ReactNode;
}
const DashboardCard = (props: DashboardCardProps) => {
  const { children, title } = props;
  return (
    <div
      className="h-full w-full 
    border border-solid border-neutral-80 bg-neutral-98
     shadow-sm shadow-neutral-60 dark:border-none dark:bg-neutral-5 dark:shadow-none"
    >
      <div className="h-full w-full px-3 py-2">
        <Typography variant="h6" color={"secondary"}>
          {title}
        </Typography>
        {children}
      </div>
    </div>
  );
};

export { DashboardCard };
