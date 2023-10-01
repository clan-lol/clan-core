"use client";
import React, { useEffect, useState } from "react";
import { VmConfig } from "@/api/model";
import { useVms } from "@/components/hooks/useVms";

import { Alert, AlertTitle, Button } from "@mui/material";

import { useSearchParams } from "next/navigation";

import { createVm, inspectVm, useGetVmLogs } from "@/api/default/default";

import { LoadingOverlay } from "./loadingOverlay";
import { FlakeBadge } from "../flakeBadge/flakeBadge";
import { Log } from "./log";
import { SubmitHandler, useForm } from "react-hook-form";
import { ConfigureVM } from "./configureVM";
import { VmBuildLogs } from "./vmBuildLogs";

interface ConfirmVMProps {
  url: string;
  handleBack: () => void;
}

export function ConfirmVM(props: ConfirmVMProps) {
  const { url, handleBack } = props;
  const formHooks = useForm<VmConfig>({
    defaultValues: {
      flake_url: url,
      flake_attr: "default",
      cores: 4,
      graphics: true,
      memory_size: 2048,
    },
  });
  const [vmUuid, setVmUuid] = useState<string | null>(null);

  const { setValue, watch, formState, handleSubmit } = formHooks;
  const { config, error, isLoading } = useVms({
    url,
    attr: watch("flake_attr"),
  });
  useEffect(() => {
    if (config) {
      setValue("cores", config?.cores);
      setValue("memory_size", config?.memory_size);
      setValue("graphics", config?.graphics);
    }
  }, [config, setValue]);

  return (
    <div className="mb-2 flex w-full max-w-2xl flex-col items-center justify-self-center pb-2">
      {!formState.isSubmitted && (
        <>
          {/* {error && (
            <Alert severity="error" className="w-full max-w-2xl">
              <AlertTitle>Error</AlertTitle>
              An Error occurred - See details below
            </Alert>
          )} */}
          <div className="mb-2 w-full max-w-2xl">
            {isLoading && (
              <LoadingOverlay
                title={"Loading VM Configuration"}
                subtitle={<FlakeBadge flakeUrl={url} flakeAttr={url} />}
              />
            )}

            <ConfigureVM formHooks={formHooks} setVmUuid={setVmUuid} />

            {/* {error && (
              <>
                <Button
                  color="error"
                  fullWidth
                  variant="contained"
                  onClick={handleBack}
                  className="my-2"
                >
                  Back
                </Button>
                <Log
                  title="Log"
                  lines={
                    error?.response?.data?.detail
                      ?.map((err, idx) => err.msg.split("\n"))
                      ?.flat()
                      .filter(Boolean) || []
                  }
                />
              </>
            )} */}
          </div>
        </>
      )}

      {formState.isSubmitted && vmUuid && <VmBuildLogs vmUuid={vmUuid} />}
    </div>
  );
}
