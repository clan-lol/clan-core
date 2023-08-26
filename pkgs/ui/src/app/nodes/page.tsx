"use client";

import NodeTable from "./NodeTable";

import Box from "@mui/material/Box";
import { tableData } from "@/data/nodeDataStatic";
import { StrictMode } from "react";

export default function Page() {
  return (
    <StrictMode>
      <NodeTable tableData={tableData} />
    </StrictMode>
  );
}
