import { callApi, SuccessData } from "@/src/api";
import {
  createForm,
  FieldValues,
  SubmitHandler,
  validate,
} from "@modular-forms/solid";
import { createQuery, useQueryClient } from "@tanstack/solid-query";
import { Typography } from "@/src/components/Typography";
import { Group } from "@/src/components/group";
import { For, Match, Show, Switch } from "solid-js";
import { TextInput } from "@/src/Form/fields";
import toast from "solid-toast";
import { useNavigate, useParams, useSearchParams } from "@solidjs/router";
import { activeURI } from "@/src/App";
import { StepProps } from "./hardware-step";

export type VarsValues = FieldValues & Record<string, Record<string, string>>;

export const VarsStep = (props: StepProps<VarsValues>) => {
  const queryClient = useQueryClient();

  const generatorsQuery = createQuery(() => ({
    queryKey: [props.dir, props.machine_id, "generators"],
    queryFn: async () => {
      const result = await callApi("get_generators_closure", {
        base_dir: props.dir,
        machine_name: props.machine_id,
      });
      if (result.status === "error") throw new Error("Failed to fetch data");
      return result.data;
    },
  }));

  const handleSubmit: SubmitHandler<VarsValues> = async (values, event) => {
    const loading_toast = toast.loading("Generating vars...");
    if (generatorsQuery.data === undefined) {
      toast.error("Error fetching data");
      return;
    }
    const result = await callApi("generate_vars_for_machine", {
      machine_name: props.machine_id,
      base_dir: props.dir,
      generators: generatorsQuery.data.map((generator) => generator.name),
      all_prompt_values: values,
    });
    queryClient.invalidateQueries({
      queryKey: [props.dir, props.machine_id, "generators"],
    });
    toast.dismiss(loading_toast);
    if (result.status === "error") {
      toast.error(result.errors[0].message);
      return;
    }
    if (result.status === "success") {
      toast.success("Vars saved successfully");
    }
    props.handleNext(values);
  };

  return (
    <Switch>
      <Match when={generatorsQuery.isLoading}>Loading ...</Match>
      <Match when={generatorsQuery.data}>
        {(generators) => (
          <VarsForm
            machine_id={props.machine_id}
            dir={props.dir}
            handleSubmit={handleSubmit}
            generators={generators()}
          />
        )}
      </Match>
    </Switch>
  );
};

export interface VarsFormProps {
  machine_id: string;
  dir: string;
  handleSubmit: SubmitHandler<VarsValues>;
  generators: SuccessData<"get_generators_closure">;
}

export const VarsForm = (props: VarsFormProps) => {
  const [formStore, { Form, Field }] = createForm<VarsValues>({});

  const handleSubmit: SubmitHandler<VarsValues> = async (values, event) => {
    console.log("Submit Vars", { values });
    // sanitize the values back (replace __dot__)
    // This hack is needed because we are using "." in the keys of the form
    const sanitizedValues = Object.fromEntries(
      Object.entries(values).map(([key, value]) => [
        key.replaceAll("__dot__", "."),
        Object.fromEntries(
          Object.entries(value).map(([k, v]) => [
            k.replaceAll("__dot__", "."),
            v,
          ]),
        ),
      ]),
    ) as VarsValues;
    const valid = await validate(formStore);
    if (!valid) {
      toast.error("Please fill all required fields");
      return;
    }
    props.handleSubmit(sanitizedValues, event);
  };

  return (
    <Form
      onSubmit={handleSubmit}
      class="flex h-full flex-col gap-6"
      noValidate={false}
    >
      <div class="max-h-[calc(100vh-20rem)] overflow-y-scroll">
        <div class="flex h-full flex-col gap-6 p-4">
          <For each={props.generators}>
            {(generator) => (
              <Group>
                <Typography hierarchy="label" size="default">
                  {generator.name}
                </Typography>
                <div>
                  Bound to module (shared): {generator.share ? "True" : "False"}
                </div>
                <For each={generator.prompts}>
                  {(prompt) => (
                    <Group>
                      <Typography hierarchy="label" size="s">
                        {!prompt.previous_value ? "Required" : "Optional"}
                      </Typography>
                      <Typography hierarchy="label" size="s">
                        {prompt.name}
                      </Typography>
                      <Field
                        // Avoid nesting issue in case of  a "."
                        name={`${generator.name.replaceAll(
                          ".",
                          "__dot__",
                        )}.${prompt.name.replaceAll(".", "__dot__")}`}
                      >
                        {(field, props) => (
                          <Switch
                            fallback={
                              <TextInput
                                inputProps={{
                                  ...props,
                                  type:
                                    prompt.prompt_type === "hidden"
                                      ? "password"
                                      : "text",
                                }}
                                label={prompt.description}
                                value={prompt.previous_value ?? ""}
                                error={field.error}
                              />
                            }
                          >
                            <Match
                              when={
                                prompt.prompt_type === "multiline" ||
                                prompt.prompt_type === "multiline-hidden"
                              }
                            >
                              <textarea
                                {...props}
                                class="w-full h-32 border border-gray-300 rounded-md p-2"
                                placeholder={prompt.description}
                                value={prompt.previous_value ?? ""}
                                name={prompt.description}
                              />
                            </Match>
                          </Switch>
                        )}
                      </Field>
                    </Group>
                  )}
                </For>
              </Group>
            )}
          </For>
        </div>
      </div>
      <button type="submit">Submit</button>
    </Form>
  );
};

export const VarsPage = () => {
  const params = useParams();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const handleNext = (values: VarsValues) => {
    if (searchParams?.action === "update") {
      navigate(`/machines/${params.id}?action=update`);
    } else {
      toast.error("Invalid action for vars page");
    }
  };
  return (
    <Show when={activeURI()}>
      {(uri) => (
        <VarsStep
          machine_id={params.id}
          dir={uri()}
          handleNext={handleNext}
          footer
        />
      )}
    </Show>
  );
};
