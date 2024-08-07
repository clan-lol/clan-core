import { Accessor, createEffect, Show } from "solid-js";
import { SuccessData } from "../api";
import { Menu } from "./Menu";
import { setRoute } from "../App";

type MachineDetails = SuccessData<"list_inventory_machines">["data"][string];

interface MachineListItemProps {
  name: string;
  info?: MachineDetails;
  nixOnly?: boolean;
}

export const MachineListItem = (props: MachineListItemProps) => {
  const { name, info, nixOnly } = props;

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
                <li>
                  <a>Deploy</a>
                </li>
              </ul>
            </Menu>
          </div>
        </div>
      </div>
    </li>
  );
};
