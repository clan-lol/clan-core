"use client";
import {
  IconButton,
  InputAdornment,
  MenuItem,
  Select,
  Typography,
} from "@mui/material";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

import { createFlake } from "@/api/flake/flake";
import { VmConfig } from "@/api/model";
import { createVm } from "@/api/vm/vm";
import { useAppState } from "@/components/hooks/useAppContext";
import { Layout } from "@/components/join/layout";
import { VmBuildLogs } from "@/components/join/vmBuildLogs";
import { ChevronRight } from "@mui/icons-material";
import { AxiosError } from "axios";
import { Controller, FormProvider, useForm } from "react-hook-form";
import { toast } from "react-hot-toast";
import { CreateForm } from "./createForm";
import { JoinForm } from "./joinForm";

export type FormValues = VmConfig & {
  workflow: "join" | "create";
  flakeUrl: string;
  dest?: string;
};

export default function JoinPrequel() {
  const queryParams = useSearchParams();
  const flakeUrl = queryParams.get("flake") || "";
  const flakeAttr = queryParams.get("attr") || "default";
  const initialParams = { flakeUrl, flakeAttr };

  const { setAppState } = useAppState();

  const methods = useForm<FormValues>({
    defaultValues: {
      flakeUrl: "",
      dest: undefined,
      workflow: "join",
      cores: 4,
      graphics: true,
      memory_size: 2048,
    },
  });

  const { control, watch, handleSubmit } = methods;

  const [vmUuid, setVmUuid] = useState<string | null>(null);
  const [showLogs, setShowLogs] = useState<boolean>(false);

  const workflow = watch("workflow");

  const WorkflowAdornment = (
    <InputAdornment position="end">
      <Controller
        name="workflow"
        control={control}
        render={({ field }) => (
          <Select
            {...field}
            label="workflow"
            variant="standard"
            disableUnderline
          >
            <MenuItem value={"join"}>Join</MenuItem>
            <MenuItem value={"create"}>Create</MenuItem>
          </Select>
        )}
      />
      <IconButton type={"submit"}>
        <ChevronRight />
      </IconButton>
    </InputAdornment>
  );
  return (
    <Layout
      header={
        <Typography
          variant="h4"
          className="w-full text-center"
          sx={{ textTransform: "capitalize" }}
        >
          {workflow}{" "}
          <Typography variant="h4" className="font-bold" component={"span"}>
            Clan.lol
          </Typography>
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
                if (workflow === "create") {
                  try {
                    await createFlake({
                      flake_name: values.dest || "default",
                      url: values.flakeUrl,
                    });
                    setAppState((s) => ({ ...s, isJoined: true }));
                  } catch (error) {
                    toast.error(
                      `Error: ${(error as AxiosError).message || ""}`,
                    );
                  }
                }
                if (workflow === "join") {
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
                    toast.error(
                      `Error: ${(error as AxiosError).message || ""}`,
                    );
                  }
                }
              })}
              className="w-full max-w-2xl justify-self-center"
            >
              {workflow == "join" && (
                <JoinForm
                  initialParams={initialParams}
                  confirmAdornment={WorkflowAdornment}
                />
              )}
              {workflow == "create" && (
                <CreateForm confirmAdornment={WorkflowAdornment} />
              )}
            </form>
          </FormProvider>
        )}
      </Suspense>
    </Layout>
  );
}
