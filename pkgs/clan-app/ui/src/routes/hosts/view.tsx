import { type Component, createSignal, For, Show } from "solid-js";
import { OperationResponse, callApi } from "@/src/api";
import { Button } from "@/src/components/button";
import Icon from "@/src/components/icon";

type ServiceModel = Extract<
  OperationResponse<"show_mdns">,
  { status: "success" }
>["data"]["services"];

export const HostList: Component = () => {
  const [services, setServices] = createSignal<ServiceModel>();

  return (
    <div>
      <div class="" data-tip="Refresh install targets">
        <Button
          variant="light"
          onClick={() => callApi("show_mdns", {})}
          startIcon={<Icon icon="Update" />}
        ></Button>
      </div>
      <div class="flex flex-wrap gap-2">
        <Show when={services()}>
          {(services) => (
            <For each={Object.values(services())}>
              {(service) => (
                <div class="w-[30rem] rounded-lg bg-white p-5 shadow-lg">
                  <div class=" flex flex-col shadow">
                    <div class="">
                      <div class="">Host</div>
                      <div class="">{service.host}</div>
                      <div class=""></div>
                    </div>

                    <div class="">
                      <div class="">IP</div>
                      <div class="">{service.ip}</div>
                      <div class=""></div>
                    </div>
                  </div>

                  <div class=" w-full px-0">
                    <div class="  ">
                      <input type="radio" name="my-accordion-4" />
                      <div class=" text-xl font-medium">Details</div>
                      <div class="">
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
