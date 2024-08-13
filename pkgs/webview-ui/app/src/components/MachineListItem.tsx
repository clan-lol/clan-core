import { Accessor, createSignal, Show } from "solid-js";
import { callApi, SuccessData } from "../api";
import { Menu } from "./Menu";
import { activeURI, setRoute } from "../App";
import toast from "solid-toast";

type MachineDetails = SuccessData<"list_inventory_machines">["data"][string];

interface MachineListItemProps {
  name: string;
  info?: MachineDetails;
  nixOnly?: boolean;
}

export const MachineListItem = (props: MachineListItemProps) => {
  const { name, info, nixOnly } = props;

  const [deploying, setDeploying] = createSignal<boolean>(false);

  return (
    <li>
      <div class="card card-side m-2 bg-base-200">
        <figure class="pl-2">
          <span
            class="material-icons content-center text-5xl"
            classList={{
              "text-neutral-500": nixOnly,
            }}
          >
            devices_other
          </span>
        </figure>
        <div class="card-body flex-row justify-between ">
          <div class="flex flex-col">
            <h2
              class="card-title"
              classList={{
                "text-neutral-500": nixOnly,
              }}
            >
              {name}
            </h2>
            <div class="text-slate-600">
              <Show when={info}>{(d) => d()?.description}</Show>
            </div>
            <div class="text-slate-600">
              <Show when={info}>
                {(d) => (
                  <>
                    <span class="material-icons text-sm">cast_connected</span>
                    {d()?.deploy.targetHost}
                  </>
                )}
              </Show>
            </div>
            <div class="flex flex-row flex-wrap gap-4 py-2"></div>
          </div>
          <div>
            <Menu
              popoverid={`menu-${props.name}`}
              label={<span class="material-icons">more_vert</span>}
            >
              <ul class="menu z-[1] w-52 rounded-box bg-base-100 p-2 shadow">
                <li>
                  <a
                    onClick={() => {
                      setRoute("machines/edit");
                    }}
                  >
                    Edit
                  </a>
                </li>
                <li
                  classList={{
                    disabled: !info?.deploy.targetHost || deploying(),
                  }}
                  onClick={async (e) => {
                    if (!info?.deploy.targetHost || deploying()) {
                      return;
                    }

                    const active_clan = activeURI();
                    if (!active_clan) {
                      toast.error("No active clan selected");
                      return;
                    }
                    if (!info?.deploy.targetHost) {
                      toast.error(
                        "Machine does not have a target host. Specify where the machine should be deployed.",
                      );
                      return;
                    }
                    setDeploying(true);
                    await toast.promise(
                      callApi("install_machine", {
                        opts: {
                          machine: name,
                          flake: {
                            loc: active_clan,
                          },
                          no_reboot: true,
                          target_host: info?.deploy.targetHost,
                          debug: true,
                          nix_options: [],
                        },
                        password: null,
                      }),
                      {
                        loading: "Deploying...",
                        success: "Deployed",
                        error: "Failed to deploy",
                      },
                    );
                    setDeploying(false);
                  }}
                >
                  <a>
                    <Show when={info?.deploy.targetHost} fallback={"Deploy"}>
                      {(d) => `Deploy to ${d()}`}
                    </Show>
                  </a>
                </li>
              </ul>
            </Menu>
          </div>
        </div>
      </div>
    </li>
  );
};
