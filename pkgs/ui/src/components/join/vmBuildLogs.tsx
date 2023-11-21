"use client";

import { useState } from "react";
import { Log } from "./log";

interface VmBuildLogsProps {
  vmUuid: string;
  handleClose: () => void;
}

export const VmBuildLogs = (props: VmBuildLogsProps) => {
  const { handleClose } = props;
  const [logs] = useState<string>("");

  return (
    <div className="w-full">
      {/* {isLoading && <LoadingOverlay title="Initializing" subtitle="" />} */}
      <Log
        lines={logs?.split("\n") || ["..."]}
        title="Building..."
        handleClose={handleClose}
      />
    </div>
  );
};
