"use client";
import React, { useState } from "react";
import { VmConfig } from "@/api/model";
import { useVms } from "@/components/hooks/useVms";
import prettyBytes from "pretty-bytes";

import {
  Alert,
  AlertTitle,
  Button,
  Chip,
  LinearProgress,
  ListSubheader,
  Switch,
  Typography,
} from "@mui/material";
import { useSearchParams } from "next/navigation";
import { toast } from "react-hot-toast";
import { Error, Numbers } from "@mui/icons-material";
import { createVm, inspectVm } from "@/api/default/default";
import { LoadingOverlay } from "./loadingOverlay";
import { FlakeBadge } from "../flakeBadge/flakeBadge";
import { Log } from "./log";

interface VmPropLabelProps {
  children: React.ReactNode;
}
const VmPropLabel = (props: VmPropLabelProps) => (
  <div className="col-span-4 flex items-center sm:col-span-1">
    {props.children}
  </div>
);

interface VmPropContentProps {
  children: React.ReactNode;
}
const VmPropContent = (props: VmPropContentProps) => (
  <div className="col-span-4 font-bold sm:col-span-3">{props.children}</div>
);

interface VmDetailsProps {
  vmConfig: VmConfig;
}

const VmDetails = (props: VmDetailsProps) => {
  const { vmConfig } = props;
  const { cores, flake_attr, flake_url, graphics, memory_size } = vmConfig;
  const [isStarting, setStarting] = useState(false);
  const handleStartVm = async () => {
    setStarting(true);
    const response = await createVm(vmConfig);
    setStarting(false);
    if (response.statusText === "OK") {
      toast.success(("VM created @ " + response?.data) as string);
    } else {
      toast.error("Could not create VM");
    }
  };
  return (
    <div className="grid grid-cols-4 gap-y-10">
      <div className="col-span-4">
        <ListSubheader>General</ListSubheader>
      </div>

      <VmPropLabel>Flake</VmPropLabel>
      <VmPropContent>
        <FlakeBadge flakeAttr={flake_attr} flakeUrl={flake_url} />
      </VmPropContent>

      <VmPropLabel>Machine</VmPropLabel>
      <VmPropContent>{flake_attr}</VmPropContent>

      <div className="col-span-4">
        <ListSubheader>VM</ListSubheader>
      </div>
      <VmPropLabel>CPU Cores</VmPropLabel>
      <VmPropContent>
        <Numbers fontSize="inherit" />
        <span className="font-bold text-black">{cores}</span>
      </VmPropContent>

      <VmPropLabel>Graphics</VmPropLabel>
      <VmPropContent>
        <Switch checked={graphics} />
      </VmPropContent>

      <VmPropLabel>Memory Size</VmPropLabel>
      <VmPropContent>{prettyBytes(memory_size * 1024 * 1024)}</VmPropContent>

      <div className="col-span-4 grid items-center">
        {isStarting && <LinearProgress />}
        <Button
          disabled={isStarting}
          variant="contained"
          onClick={handleStartVm}
        >
          Spin up VM
        </Button>
      </div>
    </div>
  );
};

interface ConfirmVMProps {
  url: string;
  attr: string;
  clanName: string;
}

export function ConfirmVM(props: ConfirmVMProps) {
  const { url, attr, clanName } = props;

  const { config, error, isLoading } = useVms({
    url,
    attr,
  });
  return (
    <>
      {error && (
        <Alert severity="error" className="w-full max-w-xl">
          <AlertTitle>Error</AlertTitle>
          An Error occurred - See details below
        </Alert>
      )}
      <div className="mb-2 w-full max-w-xl">
        {isLoading && (
          <LoadingOverlay
            title={"Loading VM Configuration"}
            subtitle={<FlakeBadge flakeUrl={url} flakeAttr={url} />}
          />
        )}
        {config && <VmDetails vmConfig={config} />}
        {error && (
          <Log
            title="Log"
            lines={
              error?.response?.data?.detail
                ?.map((err, idx) => err.msg.split("\n"))
                ?.flat()
                .filter(Boolean) || []
            }
          />
        )}
      </div>
    </>
  );
}
