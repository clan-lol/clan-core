import { callApi, OperationArgs, pyApi } from "@/src/api";
import { activeURI } from "@/src/App";
import { createForm, required } from "@modular-forms/solid";
import toast from "solid-toast";

type CreateMachineForm = OperationArgs<"create_machine">;

export function CreateMachine() {
  const [formStore, { Form, Field }] = createForm<CreateMachineForm>({});

  const handleSubmit = async (values: CreateMachineForm) => {
    const active_dir = activeURI();
    if (!active_dir) {
      toast.error("Open a clan to create the machine in");
      return;
    }

    callApi("create_machine", {
      flake: {
        loc: active_dir,
      },
      machine: {
        name: "jon",
        deploy: {
          targetHost: null,
        },
      },
    });
    console.log("submit", values);
  };
  return (
    <div class="px-1">
      Create new Machine
      <Form onSubmit={handleSubmit}>
        <Field
          name="machine.name"
          validate={[required("This field is required")]}
        >
          {(field, props) => (
            <>
              <label class="input input-bordered flex items-center gap-2">
                <input
                  type="text"
                  class="grow"
                  placeholder="name"
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
        <Field name="machine.description">
          {(field, props) => (
            <>
              <label class="input input-bordered flex items-center gap-2">
                <input
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
              <label class="input input-bordered flex items-center gap-2">
                <input
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
        <button class="btn btn-error float-right" type="submit">
          <span class="material-icons">add</span>Create
        </button>
      </Form>
    </div>
  );
}
