import { For, Show, createSignal } from "solid-js";
import { ErrorData, SuccessData, pyApi } from "../api";
import { currClanURI } from "../App";

interface MachineListItemProps {
  name: string;
}

type MachineDetails = Record<string, SuccessData<"show_machine">["data"]>;

type MachineErrors = Record<string, ErrorData<"show_machine">["errors"]>;

const [details, setDetails] = createSignal<MachineDetails>({});
const [errors, setErrors] = createSignal<MachineErrors>({});

pyApi.show_machine.receive((r) => {
  if (r.status === "error") {
    const { op_key } = r;
    if (op_key) {
      setErrors((e) => ({ ...e, [op_key]: r.errors }));
    }
    console.error(r.errors);
  }
  if (r.status === "success") {
    setDetails((d) => ({ ...d, [r.data.machine_name]: r.data }));
  }
});

export const MachineListItem = (props: MachineListItemProps) => {
  const { name } = props;

  pyApi.show_machine.dispatch({
    op_key: name,
    machine_name: name,
    flake_url: currClanURI(),
  });

  return (
    <li>
      <div class="card card-side m-2 bg-base-100 shadow-lg">
        <figure class="pl-2">
          <span class="material-icons content-center text-5xl">
            devices_other
          </span>
        </figure>
        <div class="card-body flex-row justify-between">
          <div class="flex flex-col">
            <h2 class="card-title">{name}</h2>
            <Show when={errors()[name]}>
              {(errors) => (
                <For each={errors()}>
                  {(error) => (
                    <p class="text-red-500">
                      {error.message}: {error.description}
                    </p>
                  )}
                </For>
              )}
            </Show>
            <Show when={details()[name]}>
              {(details) => (
                <p
                  classList={{
                    "text-gray-400": !details().machine_description,
                    "text-gray-600": !!details().machine_description,
                  }}
                >
                  {details().machine_description || "No description"}
                </p>
              )}
            </Show>
          </div>
          <div>
            <button class="btn btn-ghost">
              <span class="material-icons">more_vert</span>
            </button>
          </div>
        </div>
      </div>
    </li>
  );
};
