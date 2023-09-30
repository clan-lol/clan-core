"use client";
import React, { useEffect, useState } from "react";
import {
  Button,
  IconButton,
  Input,
  InputAdornment,
  Paper,
  TextField,
  Typography,
} from "@mui/material";
import { useSearchParams } from "next/navigation";
import { useInspectFlake } from "@/api/default/default";
import { ConfirmVM } from "@/components/join/confirmVM";
import { LoadingOverlay } from "@/components/join/loadingOverlay";
import { FlakeBadge } from "@/components/flakeBadge/flakeBadge";
import { Log } from "@/components/join/log";

import { useForm, SubmitHandler, Controller } from "react-hook-form";
import { Confirm } from "@/components/join/confirm";
import { Layout } from "@/components/join/layout";
import { ChevronRight } from "@mui/icons-material";

type FormValues = {
  flakeUrl: string;
  flakeAttribute: string;
};

export default function Page() {
  const queryParams = useSearchParams();
  const flakeUrl = queryParams.get("flake") || "";
  const flakeAttribute = queryParams.get("attr") || "default";
  const { handleSubmit, control, formState, getValues, reset } =
    useForm<FormValues>({ defaultValues: { flakeUrl: "" } });

  const onSubmit: SubmitHandler<FormValues> = (data) => console.log(data);

  return (
    <Layout>
      {!formState.isSubmitted && !flakeUrl && (
        <form
          onSubmit={handleSubmit(onSubmit)}
          className="w-full max-w-2xl justify-self-center"
        >
          <Controller
            name="flakeUrl"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                // variant="standard"
                // label="Clan url"
                required
                fullWidth
                startAdornment={
                  <InputAdornment position="start">Clan Url:</InputAdornment>
                }
                endAdornment={
                  <InputAdornment position="end">
                    <IconButton type="submit">
                      <ChevronRight />
                    </IconButton>
                  </InputAdornment>
                }
                // }}
              />
            )}
          />
        </form>
      )}
      {(formState.isSubmitted || flakeUrl) && (
        <Confirm
          handleBack={() => reset()}
          flakeUrl={formState.isSubmitted ? getValues("flakeUrl") : flakeUrl}
        />
      )}
    </Layout>
  );
}
