"use client";

import NodeTable from "./NodeTable";

import Box from "@mui/material/Box";
import { tableData, executeCreateData } from "@/data/nodeData";
import { StrictMode } from "react";

export default function Page() {
  return (
    <StrictMode>
      <NodeTable tableData={executeCreateData()} />
    </StrictMode>
  );
}
