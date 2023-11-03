"use client";
import { useGetVmLogs } from "@/api/vm/vm";
import { Log } from "./log";
import { LoadingOverlay } from "./loadingOverlay";

interface VmBuildLogsProps {
  vmUuid: string;
}
export const VmBuildLogs = (props: VmBuildLogsProps) => {
  const { vmUuid } = props;

  const { data: logs, isLoading } = useGetVmLogs(vmUuid as string, {
    swr: {
      enabled: vmUuid !== null,
    },
    axios: {
      responseType: "stream",
    },
  });

  return (
    <div className="w-full">
      {isLoading && <LoadingOverlay title="Initializing" subtitle="" />}
      <Log
        lines={(logs?.data as string)?.split("\n") || ["..."]}
        title="Building..."
      />
    </div>
  );
};
