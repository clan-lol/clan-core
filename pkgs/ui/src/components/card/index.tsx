import { Typography } from "@mui/material";
import { ReactNode } from "react";

interface DashboardCardProps {
  title: string;
  children?: ReactNode;
}
const DashboardCard = (props: DashboardCardProps) => {
  const { children, title } = props;
  return (
    <div className="h-full w-full bg-slate-50 shadow-sm shadow-slate-500">
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
