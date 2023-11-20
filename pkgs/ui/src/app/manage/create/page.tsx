"use client";
import { createFlake } from "@/api/flake/flake";
import { HTTPValidationError } from "@/api/model";
import { CreateClan, CreateFormValues } from "@/components/forms/createClan";
import { clanErrorToast } from "@/error/errorToast";
import { AxiosError } from "axios";
import { FormProvider, useForm } from "react-hook-form";

export default function Manage() {
  const methods = useForm<CreateFormValues>({
    defaultValues: {
      flakeDir: "",
      flakeTemplateUrl: "",
    },
  });
  const { handleSubmit } = methods;
  return (
    <FormProvider {...methods}>
      <form
        onSubmit={handleSubmit(async (values) => {
          console.log({ values });
          try {
            await createFlake(
              {
                url: values.flakeTemplateUrl,
              },
              {
                flake_dir: values.flakeDir,
              }
            );
          } catch (e) {
            const error = e as AxiosError<HTTPValidationError>;
            clanErrorToast(error);
            const maybeDetail = error?.response?.data?.detail?.[0];

            if (maybeDetail?.loc && maybeDetail?.msg) {
              const urlError = error.response?.data.detail?.find((detail) =>
                detail.loc.includes("url")
              );
              urlError &&
                methods.setError("flakeTemplateUrl", {
                  message: urlError.msg,
                });
              const flakeDirError = error.response?.data.detail?.find(
                (detail) => detail.loc.includes("flake_dir")
              );
              flakeDirError &&
                methods.setError("flakeDir", {
                  message: flakeDirError.msg,
                });
            }
          }
        })}
      >
        <CreateClan methods={methods} />
      </form>
    </FormProvider>
  );
}
