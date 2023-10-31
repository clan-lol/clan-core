"use client";
import {
  IconButton,
  Input,
  InputAdornment,
  LinearProgress,
  MenuItem,
  Select,
} from "@mui/material";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

import { createFlake } from "@/api/default/default";
import { useAppState } from "@/components/hooks/useAppContext";
import { Confirm } from "@/components/join/confirm";
import { Layout } from "@/components/join/layout";
import { ChevronRight } from "@mui/icons-material";
import { Controller, useForm } from "react-hook-form";

type FormValues = {
  workflow: "join" | "create";
  flakeUrl: string;
  dest?: string;
};

export default function JoinPrequel() {
  const queryParams = useSearchParams();
  const flakeUrl = queryParams.get("flake") || "";
  const flakeAttr = queryParams.get("attr") || "default";
  const [forkInProgress, setForkInProgress] = useState(false);
  const { setAppState } = useAppState();

  const { control, formState, getValues, reset, watch, handleSubmit } =
    useForm<FormValues>({
      defaultValues: { flakeUrl: "", dest: undefined, workflow: "join" },
    });

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
      <IconButton type="submit">
        <ChevronRight />
      </IconButton>
    </InputAdornment>
  );
  return (
    <Layout>
      <Suspense fallback="Loading">
        {!formState.isSubmitted && !flakeUrl && (
          <form
            onSubmit={handleSubmit((values) => {
              console.log("submitted", { values });
              if (workflow === "create") {
                setForkInProgress(true);
                createFlake({
                  flake_name: values.dest || "default",
                  url: values.flakeUrl,
                }).then(() => {
                  setForkInProgress(false);
                  setAppState((s) => ({ ...s, isJoined: true }));
                });
              }
            })}
            className="w-full max-w-2xl justify-self-center"
          >
            <Controller
              name="flakeUrl"
              control={control}
              render={({ field }) => (
                <Input
                  disableUnderline
                  placeholder="url"
                  color="secondary"
                  aria-required="true"
                  {...field}
                  required
                  fullWidth
                  startAdornment={
                    <InputAdornment position="start">Clan</InputAdornment>
                  }
                  endAdornment={
                    workflow == "join" ? WorkflowAdornment : undefined
                  }
                />
              )}
            />
            {workflow === "create" && (
              <Controller
                name="dest"
                control={control}
                render={({ field }) => (
                  <Input
                    sx={{ my: 2 }}
                    placeholder="Location"
                    color="secondary"
                    aria-required="true"
                    {...field}
                    required
                    fullWidth
                    startAdornment={
                      <InputAdornment position="start">Name</InputAdornment>
                    }
                    endAdornment={
                      workflow == "create" ? WorkflowAdornment : undefined
                    }
                  />
                )}
              />
            )}
          </form>
        )}
        {formState.isSubmitted && workflow == "create" && (
          <div>
            <LinearProgress />
          </div>
        )}
        {(formState.isSubmitted || flakeUrl) && workflow == "join" && (
          <Confirm
            handleBack={() => reset()}
            flakeUrl={formState.isSubmitted ? getValues("flakeUrl") : flakeUrl}
            flakeAttr={flakeAttr}
          />
        )}
      </Suspense>
    </Layout>
  );
}
