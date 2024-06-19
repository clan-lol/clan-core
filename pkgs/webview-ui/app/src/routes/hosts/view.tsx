import {
  For,
  Match,
  Show,
  Switch,
  createEffect,
  createSignal,
  type Component,
} from "solid-js";
import { useMachineContext } from "../../Config";
import { route } from "@/src/App";
import { OperationResponse, pyApi } from "@/src/api";
import toast from "solid-toast";

type ServiceModel = Extract<
  OperationResponse<"show_mdns">,
  { status: "success" }
>["data"]["services"];

export const HostList: Component = () => {
  const [services, setServices] = createSignal<ServiceModel>();

  pyApi.show_mdns.receive((r) => {
    const { status } = r;
    if (status === "error") return console.error(r.errors);
    setServices(r.data.services);
  });

  createEffect(() => {
    if (route() === "hosts") pyApi.show_mdns.dispatch({});
  });

  return (
    <div>
      <div class="tooltip" data-tip="Refresh install targets">
        <button
          class="btn btn-ghost"
          onClick={() => pyApi.show_mdns.dispatch({})}
        >
          <span class="material-icons ">refresh</span>
        </button>
      </div>
      <div class="flex gap-2 flex-wrap">
        <Show when={services()}>
          {(services) => (
            <For each={Object.values(services())}>
              {(service) => (
                <div class="rounded-lg bg-white p-5 shadow-lg w-[30rem]">
                  <div class="stats shadow flex flex-col">
                    <div class="stat">
                      <div class="stat-title">Host</div>
                      <div class="stat-value">{service.host}</div>
                      <div class="stat-desc"></div>
                    </div>

                    <div class="stat">
                      <div class="stat-title">IP</div>
                      <div class="stat-value">{service.ip}</div>
                      <div class="stat-desc"></div>
                    </div>
                  </div>

                  <div class="join join-vertical w-full px-0">
                    <div class="collapse collapse-arrow join-item">
                      <input type="radio" name="my-accordion-4" />
                      <div class="collapse-title text-xl font-medium">
                        Details
                      </div>
                      <div class="collapse-content">
                        <p>
                          <span class="font-bold">Interface</span>
                          {service.interface}
                        </p>
                        <p>
                          <span class="font-bold">Protocol</span>
                          {service.protocol}
                        </p>

                        <p>
                          <span class="font-bold">Type</span>
                          {service.type_}
                        </p>
                        <p>
                          <span class="font-bold">Domain</span>
                          {service.domain}
                        </p>
                      </div>
                    </div>
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
