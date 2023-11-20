"use client";
import { Button, Typography } from "@mui/material";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

import { VmConfig } from "@/api/model";
import { createVm } from "@/api/vm/vm";
import { Layout } from "@/components/join/layout";
import { VmBuildLogs } from "@/components/join/vmBuildLogs";
import { AxiosError } from "axios";
import { FormProvider, useForm } from "react-hook-form";
import { toast } from "react-hot-toast";
import { JoinForm } from "./joinForm";

export type FormValues = VmConfig & {
  flakeUrl: string;
  dest?: string;
};

export default function JoinPrequel() {
  const queryParams = useSearchParams();
  const flakeUrl = queryParams.get("flake") || "";
  const flakeAttr = queryParams.get("attr") || "default";
  const initialParams = { flakeUrl, flakeAttr };

  const methods = useForm<FormValues>({
    defaultValues: {
      flakeUrl: "",
      dest: undefined,
      cores: 4,
      graphics: true,
      memory_size: 2048,
    },
  });

  const { handleSubmit } = methods;

  const [vmUuid, setVmUuid] = useState<string | null>(null);
  const [showLogs, setShowLogs] = useState<boolean>(false);

  return (
    <Layout
      header={
        <Typography
          variant="h4"
          className="w-full text-center"
          sx={{ textTransform: "capitalize" }}
        >
          Clan.lol
        </Typography>
      }
    >
      <Suspense fallback="Loading">
        {vmUuid && showLogs ? (
          <VmBuildLogs vmUuid={vmUuid} handleClose={() => setShowLogs(false)} />
        ) : (
          <FormProvider {...methods}>
            <form
              onSubmit={handleSubmit(async (values) => {
                console.log("JOINING");
                console.log(values);
                try {
                  const response = await createVm({
                    cores: values.cores,
                    flake_attr: values.flake_attr,
                    flake_url: values.flakeUrl,
                    graphics: values.graphics,
                    memory_size: values.memory_size,
                  });
                  const { uuid } = response?.data || null;
                  setShowLogs(true);
                  setVmUuid(() => uuid);
                  if (response.statusText === "OK") {
                    toast.success(("Joined @ " + uuid) as string);
                  } else {
                    toast.error("Could not join");
                  }
                } catch (error) {
                  toast.error(`Error: ${(error as AxiosError).message || ""}`);
                }
              })}
              className="w-full max-w-2xl justify-self-center"
            >
              <JoinForm initialParams={initialParams} />
              <Button type="submit">Join</Button>
            </form>
          </FormProvider>
        )}
      </Suspense>
    </Layout>
  );
}
