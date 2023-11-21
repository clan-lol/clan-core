"use client";
import { Button, Typography } from "@mui/material";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

import { Layout } from "@/components/join/layout";
import { FormProvider, useForm } from "react-hook-form";
import { JoinForm } from "./joinForm";

export type FormValues = {
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
    },
  });

  const { handleSubmit } = methods;

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
        {
          <FormProvider {...methods}>
            <form
              onSubmit={handleSubmit(async (values) => {
                console.log("JOINING");
                console.log(values);
              })}
              className="w-full max-w-2xl justify-self-center"
            >
              <JoinForm initialParams={initialParams} />
              <Button type="submit">Join</Button>
            </form>
          </FormProvider>
        }
      </Suspense>
    </Layout>
  );
}
