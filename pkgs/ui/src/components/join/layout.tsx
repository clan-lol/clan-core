"use client";
import { ReactNode } from "react";

interface LayoutProps {
  children: ReactNode;
  header: ReactNode;
}
export const Layout = (props: LayoutProps) => {
  return (
    <div className="grid h-[70vh] w-full grid-cols-1 justify-center gap-y-4">
      {props.header}
      {props.children}
    </div>
  );
};
