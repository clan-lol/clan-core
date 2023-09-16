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

interface FlakeBadgeProps {
  flakeUrl: string;
  flakeAttr: string;
}
const FlakeBadge = (props: FlakeBadgeProps) => (
  <Chip
    color="secondary"
    label={`${props.flakeUrl}#${props.flakeAttr}`}
    sx={{ p: 2 }}
  />
);

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

interface ErrorLogOptions {
  lines: string[];
}
const ErrorLog = (props: ErrorLogOptions) => {
  const { lines } = props;
  return (
    <div className="w-full bg-slate-800 p-4 text-white shadow-inner shadow-black">
      <div className="mb-1 text-slate-400">Log</div>
      {lines.map((item, idx) => (
        <span key={`${idx}`} className="mb-2 block break-words">
          {item}
          <br />
        </span>
      ))}
    </div>
  );
};

export default function Page() {
  const queryParams = useSearchParams();
  const flakeUrl = queryParams.get("flake") || "";
  const flakeAttribute = queryParams.get("attr") || "default";

  const { config, error, isLoading } = useVms({
    url: flakeUrl,
    attr: flakeAttribute,
  });
  const clanName = "Lassul.us";
  return (
    <div className="grid h-[70vh] w-full place-items-center gap-y-4">
      <Typography variant="h4" className="w-full text-center">
        Join{" "}
        <Typography variant="h4" className="font-bold" component={"span"}>
          {clanName}
        </Typography>
        {"' "}
        Clan
      </Typography>
      {error && (
        <Alert severity="error" className="w-full max-w-xl">
          <AlertTitle>Error</AlertTitle>
          An Error occurred - See details below
        </Alert>
      )}
      <div className="w-full max-w-xl">
        {isLoading && (
          <div className="w-full">
            <Typography variant="subtitle2">Loading Flake</Typography>
            <LinearProgress className="mb-2 w-full" />
            <div className="grid w-full place-items-center">
              <FlakeBadge flakeUrl={flakeUrl} flakeAttr={flakeAttribute} />
            </div>

            <Typography variant="subtitle1"></Typography>
          </div>
        )}
        {(!flakeUrl || !flakeAttribute) && <div>Invalid URL</div>}
        {config && <VmDetails vmConfig={config} />}
        {error && (
          <ErrorLog
            lines={
              error?.response?.data?.detail
                ?.map((err, idx) => err.msg.split("\n"))
                ?.flat()
                .filter(Boolean) || []
            }
          />
        )}
      </div>
    </div>
  );
}
