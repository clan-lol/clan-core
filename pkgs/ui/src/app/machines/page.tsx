"use client";

import { tableData } from "@/data/nodeDataStatic";
import { StrictMode } from "react";
import { NodeTable } from "@/components/table";
import { useMachines } from "@/components/hooks/useMachines";

export default function Page() {
  //const { data, isLoading } = useMachines();
  //console.log({ data, isLoading });
  return (
    <StrictMode>
      <NodeTable tableData={tableData} />
    </StrictMode>
  );
}
