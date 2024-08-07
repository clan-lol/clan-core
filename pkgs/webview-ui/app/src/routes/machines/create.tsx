import { callApi, OperationArgs, pyApi, OperationResponse } from "@/src/api";
import { activeURI, setRoute } from "@/src/App";
import { TextInput } from "@/src/components/TextInput";
import { createForm, required, reset } from "@modular-forms/solid";
import { createQuery, useQueryClient } from "@tanstack/solid-query";
import { Match, Switch } from "solid-js";
import toast from "solid-toast";

type CreateMachineForm = OperationArgs<"create_machine">;

export function CreateMachine() {
  const [formStore, { Form, Field }] = createForm<CreateMachineForm>({
    initialValues: {
      flake: {
        loc: activeURI() || "",
      },
      machine: {
        deploy: {
          targetHost: "",
        },
        name: "",
        description: "",
      },
    },
  });

  const queryClient = useQueryClient();

  const handleSubmit = async (values: CreateMachineForm) => {
    const active_dir = activeURI();
    if (!active_dir) {
      toast.error("Open a clan to create the machine within");
      return;
    }

    console.log("submitting", values);

    const response = await callApi("create_machine", {
      ...values,
      flake: {
        loc: active_dir,
      },
    });

    if (response.status === "success") {
      toast.success(`Successfully created ${values.machine.name}`);
      reset(formStore);

      queryClient.invalidateQueries({
        queryKey: [activeURI(), "list_machines"],
      });
      setRoute("machines");
    } else {
      toast.error(
        `Error: ${response.errors[0].message}. Machine ${values.machine.name} could not be created`,
      );
    }
  };
  return (
    <div class="px-1">
      <span class="px-2">Create new Machine</span>
      <Form onSubmit={handleSubmit}>
        <Field
          name="machine.name"
          validate={[required("This field is required")]}
        >
          {(field, props) => (
            <TextInput
              inputProps={props}
              formStore={formStore}
              value={`${field.value}`}
              label={"name"}
              error={field.error}
              required
            />
          )}
        </Field>
        <Field name="machine.description">
          {(field, props) => (
            <TextInput
              inputProps={props}
              formStore={formStore}
              value={`${field.value}`}
              label={"description"}
              error={field.error}
            />
          )}
        </Field>
        <Field name="machine.deploy.targetHost">
          {(field, props) => (
            <>
              <TextInput
                inputProps={props}
                formStore={formStore}
                value={`${field.value}`}
                label={"Deployment target"}
                error={field.error}
              />
              <div class="label">
                <span class="label-text-alt text-neutral">
                  Must be set before deployment for the following tasks:
                  <ul>
                    <li>
                      <span>Detect hardware config</span>
                    </li>
                    <li>
                      <span>Detect disk layout</span>
                    </li>
                    <li>
                      <span>Remote installation</span>
                    </li>
                  </ul>
                </span>
              </div>
            </>
          )}
        </Field>
        <button
          class="btn btn-error float-right"
          type="submit"
          classList={{
            "btn-disabled": formStore.submitting,
          }}
        >
          <Switch
            fallback={
              <>
                <span class="loading loading-spinner loading-sm"></span>Creating
              </>
            }
          >
            <Match when={!formStore.submitting}>
              <span class="material-icons">add</span>Create
            </Match>
          </Switch>
        </button>
      </Form>
    </div>
  );
}
