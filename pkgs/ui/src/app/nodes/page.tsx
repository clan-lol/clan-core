"use client";

import NodeList from "./NodeList";

import Box from "@mui/material/Box";
import { tableData } from "@/data/nodeData";

export default function Page() {
  return (
    <Box
      sx={{ backgroundColor: "#e9ecf5", height: "100%", width: "100%" }}
      display="inline-block"
      id="rootBox"
    >
      <NodeList tableData={tableData} />
    </Box>
  );
}
