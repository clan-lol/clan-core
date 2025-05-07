import { callApi } from "@/src/api";
import {
  createForm,
  SubmitHandler,
  validate,
  FieldValues,
} from "@modular-forms/solid";
import { createQuery, useQueryClient } from "@tanstack/solid-query";
import { Typography } from "@/src/components/Typography";
import { Group } from "@/src/components/group";
import { For, Match, Show, Switch } from "solid-js";
import { TextInput } from "@/src/Form/fields";
import toast from "solid-toast";
import { useNavigate, useParams } from "@solidjs/router";
import { activeURI } from "@/src/App";

export type VarsValues = FieldValues & Record<string, Record<string, string>>;

export interface VarsStepProps {
  machine_id: string;
  dir: string;
}

export const VarsStep = (props: VarsStepProps) => {
  const [formStore, { Form, Field }] = createForm<VarsValues>({});

  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const handleSubmit: SubmitHandler<VarsValues> = async (values, event) => {
    console.log("Submit Disk", { values });
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
    if (generatorsQuery.data === undefined) {
      toast.error("Error fetching data");
      return;
    }
    const loading_toast = toast.loading("Generating vars...");
    const result = await callApi("generate_vars_for_machine", {
      machine_name: props.machine_id,
      base_dir: props.dir,
      generators: generatorsQuery.data.map((generator) => generator.name),
      all_prompt_values: sanitizedValues,
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
      navigate(`/machines/${props.machine_id}?action=update`);
    }
  };

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

  return (
    <Form
      onSubmit={handleSubmit}
      class="flex h-full flex-col gap-6"
      noValidate={false}
    >
      <div class="max-h-[calc(100vh-20rem)] overflow-y-scroll">
        <div class="flex h-full flex-col gap-6 p-4">
          <Switch>
            <Match when={generatorsQuery.isLoading}>Loading ...</Match>
            <Match when={generatorsQuery.data}>
              {(generators) => (
                <For each={generators()}>
                  {(generator) => (
                    <Group>
                      <Typography hierarchy="label" size="default">
                        {generator.name}
                      </Typography>
                      <div>
                        Bound to module (shared):{" "}
                        {generator.share ? "True" : "False"}
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
                            {/* Avoid nesting issue in case of a "." */}
                            <Field
                              name={`${generator.name.replaceAll(".", "__dot__")}.${prompt.name.replaceAll(".", "__dot__")}`}
                            >
                              {(field, props) => (
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
                              )}
                            </Field>
                          </Group>
                        )}
                      </For>
                    </Group>
                  )}
                </For>
              )}
            </Match>
          </Switch>
        </div>
      </div>
      <button type="submit">Submit</button>
    </Form>
  );
};

export const VarsForMachine = () => {
  const params = useParams();

  return (
    <Show when={activeURI()}>
      {(uri) => <VarsStep machine_id={params.id} dir={uri()} />}
    </Show>
  );
};
