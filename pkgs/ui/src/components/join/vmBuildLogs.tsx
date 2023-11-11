"use client";

import { getGetVmLogsKey } from "@/api/vm/vm";
import axios from "axios";
import { Dispatch, SetStateAction, useEffect, useState } from "react";
import { Log } from "./log";

interface VmBuildLogsProps {
  vmUuid: string;
  handleClose: () => void;
}

const streamLogs = async (
  uuid: string,
  setter: Dispatch<SetStateAction<string>>,
  onFinish: () => void,
) => {
  const apiPath = getGetVmLogsKey(uuid);
  const baseUrl = axios.defaults.baseURL;

  const response = await fetch(`${baseUrl}${apiPath}`);
  const reader = response?.body?.getReader();
  if (!reader) {
    console.log("could not get reader");
  }
  while (true) {
    const stream = await reader?.read();
    if (!stream || stream.done) {
      console.log("stream done");
      onFinish();
      break;
    }

    const text = new TextDecoder().decode(stream.value);
    setter((s) => `${s}${text}`);
    console.log("Received", stream.value);
    console.log("String:", text);
  }
};

export const VmBuildLogs = (props: VmBuildLogsProps) => {
  const { vmUuid, handleClose } = props;
  const [logs, setLogs] = useState<string>("");
  const [done, setDone] = useState<boolean>(false);

  // Reset the logs if uuid changes
  useEffect(() => {
    setLogs("");
    setDone(false);
  }, [vmUuid]);

  !done && streamLogs(vmUuid, setLogs, () => setDone(true));

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
