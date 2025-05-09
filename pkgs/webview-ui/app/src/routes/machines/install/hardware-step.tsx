import { callApi } from "@/src/api";
import { activeURI } from "@/src/App";
import { Button } from "@/src/components/button";
import Icon from "@/src/components/icon";
import { InputError, InputLabel } from "@/src/components/inputBase";
import { FieldLayout } from "@/src/Form/fields/layout";
import {
  createForm,
  SubmitHandler,
  FieldValues,
  validate,
  required,
  getValue,
  submit,
  setValue,
} from "@modular-forms/solid";
import { createEffect, createSignal, JSX, Match, Switch } from "solid-js";
import { TextInput } from "@/src/Form/fields";
import { createQuery } from "@tanstack/solid-query";
import { Badge } from "@/src/components/badge";
import { Group } from "@/src/components/group";
import {
  FileSelectorField,
  type FileDialogOptions,
} from "@/src/components/fileSelect";

export type HardwareValues = FieldValues & {
  report: boolean;
  target: string;
  sshKey?: File;
};

export interface StepProps<T> {
  machine_id: string;
  dir: string;
  handleNext: (data: T) => void;
  footer: JSX.Element;
  initial?: T;
}
export const HWStep = (props: StepProps<HardwareValues>) => {
  const [formStore, { Form, Field }] = createForm<HardwareValues>({
    initialValues: (props.initial as HardwareValues) || {},
  });

  const handleSubmit: SubmitHandler<HardwareValues> = async (values, event) => {
    console.log("Submit Hardware", { values });
    const valid = await validate(formStore);
    console.log("Valid", valid);
    if (!valid) return;
    props.handleNext(values);
  };

  const [isGenerating, setIsGenerating] = createSignal(false);

  const hwReportQuery = createQuery(() => ({
    queryKey: [props.dir, props.machine_id, "hw_report"],
    queryFn: async () => {
      const result = await callApi("show_machine_hardware_config", {
        machine: {
          flake: {
            identifier: props.dir,
          },
          name: props.machine_id,
        },
      });
      if (result.status === "error") throw new Error("Failed to fetch data");
      return result.data;
    },
  }));
  // Workaround to set the form state
  createEffect(() => {
    const report = hwReportQuery.data;
    if (report === "nixos-facter" || report === "nixos-generate-config") {
      setValue(formStore, "report", true);
    }
  });

  const generateReport = async (e: Event) => {
    const curr_uri = activeURI();
    if (!curr_uri) return;

    await validate(formStore, "target");
    const target = getValue(formStore, "target");
    const sshFile = getValue(formStore, "sshKey") as File | undefined;

    if (!target) {
      console.error("Target is not set");
      return;
    }

    const r = await callApi("generate_machine_hardware_info", {
      opts: {
        machine: {
          name: props.machine_id,
          override_target_host: target,
          private_key: sshFile?.name,
          flake: {
            identifier: curr_uri,
          },
        },
        backend: "nixos-facter",
      },
    });

    // TODO: refresh the machine details

    hwReportQuery.refetch();
    submit(formStore);
  };

  return (
    <Form onSubmit={handleSubmit} class="flex flex-col gap-6">
      <div class="max-h-[calc(100vh-20rem)] overflow-y-scroll">
        <div class="flex h-full flex-col gap-6 p-4">
          <Group>
            <Field name="target" validate={required("Target must be provided")}>
              {(field, fieldProps) => (
                <TextInput
                  error={field.error}
                  variant="ghost"
                  label="Target ip"
                  value={field.value || ""}
                  inputProps={fieldProps}
                  required
                />
              )}
            </Field>
            <FileSelectorField
              Field={Field}
              name="sshKey" // Corresponds to FlashFormValues.sshKeys
              label="SSH Private Key"
              description="Provide your SSH private key for secure, passwordless connections."
              multiple={false}
              fileDialogOptions={
                {
                  title: "Select SSH Keys",
                  initial_folder: "~/.ssh",
                } as FileDialogOptions
              }
              // You could add custom validation via modular-forms 'validate' prop on CustomFileField if needed
              // e.g. validate={[required("At least one SSH key is required.")]}
              // This would require CustomFileField to accept and pass `validate` to its internal `Field`.
            />
          </Group>
          <Group>
            <Field
              name="report"
              type="boolean"
              validate={required("Report must be generated")}
            >
              {(field, fieldProps) => (
                <FieldLayout
                  error={field.error && <InputError error={field.error} />}
                  label={
                    <InputLabel
                      required
                      help="Detect hardware specific drivers from target ip"
                    >
                      Hardware report
                    </InputLabel>
                  }
                  field={
                    <Switch>
                      <Match when={hwReportQuery.isLoading}>
                        <div>Loading...</div>
                      </Match>
                      <Match when={hwReportQuery.error}>
                        <div>Error...</div>
                      </Match>
                      <Match when={hwReportQuery.data}>
                        {(data) => (
                          <>
                            <Switch>
                              <Match when={data() === "none"}>
                                <Badge color="red" icon="Attention">
                                  No report
                                </Badge>
                                <Button
                                  variant="ghost"
                                  disabled={isGenerating()}
                                  startIcon={<Icon icon="Report" />}
                                  class="w-full"
                                  onClick={generateReport}
                                >
                                  Run hardware detection
                                </Button>
                              </Match>
                              <Match when={data() === "nixos-facter"}>
                                <Badge color="primary" icon="Checkmark">
                                  Report detected
                                </Badge>
                                <Button
                                  variant="ghost"
                                  disabled={isGenerating()}
                                  startIcon={<Icon icon="Report" />}
                                  class="w-full"
                                  onClick={generateReport}
                                >
                                  Re-run hardware detection
                                </Button>
                              </Match>
                              <Match when={data() === "nixos-generate-config"}>
                                <Badge color="primary" icon="Checkmark">
                                  Legacy Report detected
                                </Badge>
                                <Button
                                  variant="ghost"
                                  disabled={isGenerating()}
                                  startIcon={<Icon icon="Report" />}
                                  class="w-full"
                                  onClick={generateReport}
                                >
                                  Replace hardware detection
                                </Button>
                              </Match>
                            </Switch>
                          </>
                        )}
                      </Match>
                    </Switch>
                  }
                />
              )}
            </Field>
          </Group>
        </div>
      </div>
      {props.footer}
    </Form>
  );
};
