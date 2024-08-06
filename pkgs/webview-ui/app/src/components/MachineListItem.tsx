import { createSignal, Match, Show, Switch } from "solid-js";
import { ErrorData, pyApi, SuccessData } from "../api";

type MachineDetails = SuccessData<"list_inventory_machines">["data"][string];

interface MachineListItemProps {
  name: string;
  info?: MachineDetails;
}

type HWInfo = Record<string, SuccessData<"show_machine_hardware_info">["data"]>;
type DeploymentInfo = Record<
  string,
  SuccessData<"show_machine_deployment_target">["data"]
>;

type MachineErrors = Record<string, ErrorData<"show_machine">["errors"]>;

const [hwInfo, setHwInfo] = createSignal<HWInfo>({});

const [deploymentInfo, setDeploymentInfo] = createSignal<DeploymentInfo>({});

const [errors, setErrors] = createSignal<MachineErrors>({});

// pyApi.show_machine_hardware_info.receive((r) => {
//   const { op_key } = r;
//   if (r.status === "error") {
//     console.error(r.errors);
//     if (op_key) {
//       setHwInfo((d) => ({ ...d, [op_key]: { system: null } }));
//     }
//     return;
//   }
//   if (op_key) {
//     setHwInfo((d) => ({ ...d, [op_key]: r.data }));
//   }
// });

// pyApi.show_machine_deployment_target.receive((r) => {
//   const { op_key } = r;
//   if (r.status === "error") {
//     console.error(r.errors);
//     if (op_key) {
//       setDeploymentInfo((d) => ({ ...d, [op_key]: null }));
//     }
//     return;
//   }
//   if (op_key) {
//     setDeploymentInfo((d) => ({ ...d, [op_key]: r.data }));
//   }
// });

export const MachineListItem = (props: MachineListItemProps) => {
  const { name, info } = props;

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
            <div class="text-slate-600">
              <Show when={info}>{(d) => d()?.description}</Show>
            </div>
            <div class="flex flex-row flex-wrap gap-4 py-2"></div>
            {/* Show only the first error at the bottom */}
            <Show when={errors()[name]?.[0]}>
              {(error) => (
                <div class="badge badge-error py-4">
                  Error: {error().message}: {error().description}
                </div>
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
