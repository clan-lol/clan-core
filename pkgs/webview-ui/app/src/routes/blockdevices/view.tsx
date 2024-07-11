import { route } from "@/src/App";
import { OperationResponse, pyApi } from "@/src/api";
import { Component, For, Show, createEffect, createSignal } from "solid-js";

type DevicesModel = Extract<
  OperationResponse<"show_block_devices">,
  { status: "success" }
>["data"]["blockdevices"];

export const BlockDevicesView: Component = () => {
  const [devices, setDevices] = createSignal<DevicesModel>();

  // pyApi.show_block_devices.receive((r) => {
  //   const { status } = r;
  //   if (status === "error") return console.error(r.errors);
  //   setServices(r.data.blockdevices);
  // });

  // createEffect(() => {
  //   if (route() === "blockdevices") pyApi.show_block_devices.dispatch({});
  // });

  return (
    <div>
      <div class="tooltip tooltip-bottom" data-tip="Refresh">
        <button
          class="btn btn-ghost"
          // onClick={() => pyApi.show_block_devices.dispatch({})}
        >
          <span class="material-icons ">refresh</span>
        </button>
      </div>
      <div class="flex max-w-screen-lg flex-col gap-4">
        <Show when={devices()}>
          {(devices) => (
            <For each={devices()}>
              {(device) => (
                <div class="stats shadow">
                  <div class="stat w-28 py-8">
                    <div class="stat-title">Name</div>
                    <div class="stat-value">
                      {" "}
                      <span class="material-icons">storage</span> {device.name}
                    </div>
                    <div class="stat-desc"></div>
                  </div>

                  <div class="stat w-28">
                    <div class="stat-title">Size</div>
                    <div class="stat-value">{device.size}</div>
                    <div class="stat-desc"></div>
                  </div>
                </div>
              )}
            </For>
          )}
        </Show>
      </div>
    </div>
  );
};
