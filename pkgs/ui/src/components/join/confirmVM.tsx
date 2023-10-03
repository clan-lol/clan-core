"use client";
import React, { useEffect, useState } from "react";
import { VmConfig } from "@/api/model";
import { useVms } from "@/components/hooks/useVms";

import { LoadingOverlay } from "./loadingOverlay";
import { useForm } from "react-hook-form";
import { ConfigureVM } from "./configureVM";
import { VmBuildLogs } from "./vmBuildLogs";

interface ConfirmVMProps {
  url: string;
  handleBack: () => void;
  defaultFlakeAttr: string;
}

export function ConfirmVM(props: ConfirmVMProps) {
  const { url, defaultFlakeAttr } = props;
  const formHooks = useForm<VmConfig>({
    defaultValues: {
      flake_url: url,
      flake_attr: defaultFlakeAttr,
      cores: 4,
      graphics: true,
      memory_size: 2048,
    },
  });
  const [vmUuid, setVmUuid] = useState<string | null>(null);

  const { setValue, watch, formState } = formHooks;
  const { config, isLoading } = useVms({
    url,
    attr: watch("flake_attr") || defaultFlakeAttr,
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
          <div className="mb-2 w-full max-w-2xl">
            {isLoading && (
              <LoadingOverlay title={"Loading VM Configuration"} subtitle="" />
            )}

            <ConfigureVM formHooks={formHooks} setVmUuid={setVmUuid} />
          </div>
        </>
      )}

      {formState.isSubmitted && vmUuid && <VmBuildLogs vmUuid={vmUuid} />}
    </div>
  );
}
