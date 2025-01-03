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
import toast from "solid-toast";
import { Group } from "../details";
import { TextInput } from "@/src/Form/fields";
import { createQuery } from "@tanstack/solid-query";

interface Hardware extends FieldValues {
  report: boolean;
  target: string;
}

export interface StepProps {
  machine_id: string;
  dir: string;
  handleNext: () => void;
  footer: JSX.Element;
  initial?: Partial<Hardware>;
}
export const HWStep = (props: StepProps) => {
  const [formStore, { Form, Field }] = createForm<Hardware>({
    initialValues: props.initial || {},
  });

  const handleSubmit: SubmitHandler<Hardware> = async (values, event) => {
    console.log("Submit Hardware", { values });
    const valid = await validate(formStore);
    console.log("Valid", valid);
    if (!valid) return;
    props.handleNext();
  };

  const [isGenerating, setIsGenerating] = createSignal(false);

  const hwReportQuery = createQuery(() => ({
    queryKey: [props.dir, props.machine_id, "hw_report"],
    queryFn: async () => {
      const result = await callApi("show_machine_hardware_config", {
        clan_dir: props.dir,
        machine_name: props.machine_id,
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

    const loading_toast = toast.loading("Generating hardware report...");

    await validate(formStore, "target");
    const target = getValue(formStore, "target");

    if (!target) {
      toast.error("Target ip must be provided");
      return;
    }
    setIsGenerating(true);
    const r = await callApi("generate_machine_hardware_info", {
      opts: {
        flake: { loc: curr_uri },
        machine: props.machine_id,
        target_host: target,
        backend: "nixos-facter",
      },
    });
    setIsGenerating(false);
    toast.dismiss(loading_toast);
    // TODO: refresh the machine details

    if (r.status === "error") {
      toast.error(`Failed to generate report. ${r.errors[0].message}`);
    }
    if (r.status === "success") {
      toast.success("Report generated successfully");
    }
    hwReportQuery.refetch();
    submit(formStore);
  };

  return (
    <Form onSubmit={handleSubmit} class="flex flex-col gap-6">
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
                            <Button
                              disabled={isGenerating()}
                              startIcon={<Icon icon="Report" />}
                              class="w-full"
                              onClick={generateReport}
                            >
                              Run hardware report
                            </Button>
                          </Match>
                          <Match when={data() === "nixos-facter"}>
                            <div>Detected</div>
                          </Match>
                          <Match when={data() === "nixos-generate-config"}>
                            <div>Nixos report Detected</div>
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
      {props.footer}
    </Form>
  );
};