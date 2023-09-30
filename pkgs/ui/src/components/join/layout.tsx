"use client";
import { Typography } from "@mui/material";
import { ReactNode } from "react";

interface LayoutProps {
  children: ReactNode;
}
export const Layout = (props: LayoutProps) => {
  return (
    <div className="grid h-[70vh] w-full grid-cols-1 justify-center gap-y-4">
      <Typography variant="h4" className="w-full text-center">
        Join{" "}
        <Typography variant="h4" className="font-bold" component={"span"}>
          Clan.lol
        </Typography>
      </Typography>
      {props.children}
    </div>
  );
};
