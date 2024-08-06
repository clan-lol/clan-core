import { callApi, OperationArgs, pyApi, OperationResponse } from "@/src/api";
import { activeURI, setRoute } from "@/src/App";
import { createForm, required, reset } from "@modular-forms/solid";
import { createQuery } from "@tanstack/solid-query";
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

  const { refetch: refetchMachines } = createQuery(() => ({
    queryKey: [activeURI(), "list_inventory_machines"],
  }));

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
      refetchMachines();
      setRoute("machines");
    } else {
      toast.error(
        `Error: ${response.errors[0].message}. Machine ${values.machine.name} could not be created`,
      );
    }
  };
  return (
    <div class="px-1">
      Create new Machine
      <button
        onClick={() => {
          reset(formStore);
        }}
      >
        reset
      </button>
      <Form onSubmit={handleSubmit}>
        <Field
          name="machine.name"
          validate={[required("This field is required")]}
        >
          {(field, props) => (
            <>
              <label
                class="input input-bordered flex items-center gap-2"
                classList={{
                  "input-disabled": formStore.submitting,
                }}
              >
                <input
                  {...props}
                  value={field.value}
                  type="text"
                  class="grow"
                  placeholder="name"
                  required
                  disabled={formStore.submitting}
                />
              </label>
              <div class="label">
                {field.error && (
                  <span class="label-text-alt font-bold text-error">
                    {field.error}
                  </span>
                )}
              </div>
            </>
          )}
        </Field>
        <Field name="machine.description">
          {(field, props) => (
            <>
              <label
                class="input input-bordered flex items-center gap-2"
                classList={{
                  "input-disabled": formStore.submitting,
                }}
              >
                <input
                  value={String(field.value)}
                  type="text"
                  class="grow"
                  placeholder="description"
                  required
                  {...props}
                />
              </label>
              <div class="label">
                {field.error && (
                  <span class="label-text-alt font-bold text-error">
                    {field.error}
                  </span>
                )}
              </div>
            </>
          )}
        </Field>
        <Field name="machine.deploy.targetHost">
          {(field, props) => (
            <>
              <label
                class="input input-bordered flex items-center gap-2"
                classList={{
                  "input-disabled": formStore.submitting,
                }}
              >
                <input
                  value={String(field.value)}
                  type="text"
                  class="grow"
                  placeholder="root@flash-installer.local"
                  required
                  {...props}
                />
              </label>
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
                {field.error && (
                  <span class="label-text-alt font-bold text-error">
                    {field.error}
                  </span>
                )}
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
