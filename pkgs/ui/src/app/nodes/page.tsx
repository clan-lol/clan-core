"use client";

import NodeList from "./NodeList";

import Box from "@mui/material/Box";
import { tableData } from "@/data/nodeData";
import { StrictMode } from "react";

export default function Page() {
  return (
      <StrictMode>
      <NodeList tableData={tableData} />
      </StrictMode>
  );
}
