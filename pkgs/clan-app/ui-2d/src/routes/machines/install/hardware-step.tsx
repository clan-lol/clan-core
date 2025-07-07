import { callApi } from "@/src/api";
import { Button } from "../../../components/Button/Button";
import Icon from "@/src/components/icon";
import { InputError, InputLabel } from "@/src/components/inputBase";
import { FieldLayout } from "@/src/Form/fields/layout";
import {
  createForm,
  FieldValues,
  required,
  setValue,
  submit,
  SubmitHandler,
  validate,
} from "@modular-forms/solid";
import { createEffect, createSignal, JSX, Match, Switch } from "solid-js";
import { useQuery } from "@tanstack/solid-query";
import { Badge } from "@/src/components/badge";
import { Group } from "@/src/components/group";
import { useClanContext } from "@/src/contexts/clan";
import { RemoteForm, type RemoteData } from "@/src/components/RemoteForm";

export type HardwareValues = FieldValues & {
  report: boolean;
  target: string;
  remoteData: RemoteData;
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

  // Initialize remote data from existing target or create new default
  const [remoteData, setRemoteData] = createSignal<RemoteData>({
    address: props.initial?.target || "",
    user: "root",
    command_prefix: "sudo",
    port: 22,
    forward_agent: false,
    host_key_check: "ask", // 0 = ASK
    verbose_ssh: false,
    ssh_options: {},
    tor_socks: false,
  });

  const handleSubmit: SubmitHandler<HardwareValues> = async (values, event) => {
    console.log("Submit Hardware", { values });
    const valid = await validate(formStore);
    console.log("Valid", valid);
    if (!valid) return;

    // Include remote data in the values
    const submitValues = {
      ...values,
      remoteData: remoteData(),
      target: remoteData().address, // Keep target for backward compatibility
    };

    props.handleNext(submitValues);
  };

  const [isGenerating, setIsGenerating] = createSignal(false);

  const hwReportQuery = useQuery(() => ({
    queryKey: [props.dir, props.machine_id, "hw_report"],
    queryFn: async () => {
      const result = await callApi("describe_machine_hardware", {
        machine: {
          flake: {
            identifier: props.dir,
          },
          name: props.machine_id,
        },
      }).promise;
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

  const { activeClanURI } = useClanContext();

  const generateReport = async (e: Event) => {
    const currentRemoteData = remoteData();
    if (!currentRemoteData.address) {
      console.error("Target address is not set");
      return;
    }

    const active_clan = activeClanURI();
    if (!active_clan) {
      console.error("No active clan selected");
      return;
    }

    const target_host = await callApi("get_host", {
      field: "targetHost",
      flake: { identifier: active_clan },
      name: props.machine_id,
    }).promise;

    if (target_host.status == "error") {
      console.error("No target host found for the machine");
      return;
    }

    if (target_host.data === null) {
      console.error("No target host found for the machine");
      return;
    }

    if (!target_host.data!.data) {
      console.error("No target host found for the machine");
      return;
    }

    const r = await callApi("generate_machine_hardware_info", {
      opts: {
        machine: {
          name: props.machine_id,
          flake: {
            identifier: active_clan,
          },
        },
        backend: "nixos-facter",
      },
      target_host: target_host.data!.data,
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
            <RemoteForm
              showSave={false}
              machine={{
                name: props.machine_id,
                flake: {
                  identifier: props.dir,
                },
              }}
              field="targetHost"
            />
            {/* Hidden field for form validation */}
            <Field name="target">
              {(field, fieldProps) => (
                <input
                  {...fieldProps}
                  type="hidden"
                  value={remoteData().address}
                />
              )}
            </Field>
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
