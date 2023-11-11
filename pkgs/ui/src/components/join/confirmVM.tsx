"use client";
import { useVms } from "@/components/hooks/useVms";
import { useEffect } from "react";

import { FormValues } from "@/views/joinPrequel";
import { useFormContext } from "react-hook-form";
import { ConfigureVM } from "./configureVM";
import { LoadingOverlay } from "./loadingOverlay";

interface ConfirmVMProps {
  url: string;
  handleBack: () => void;
  defaultFlakeAttr: string;
}

export function ConfirmVM(props: ConfirmVMProps) {
  const formHooks = useFormContext<FormValues>();

  const { setValue, watch } = formHooks;

  const url = watch("flakeUrl");
  const attr = watch("flake_attr");

  const { config, isLoading } = useVms({
    url,
    attr,
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
      <div className="mb-2 w-full max-w-2xl">
        {isLoading && (
          <LoadingOverlay title={"Loading VM Configuration"} subtitle="" />
        )}

        <ConfigureVM formHooks={formHooks} />
      </div>
    </div>
  );
}
