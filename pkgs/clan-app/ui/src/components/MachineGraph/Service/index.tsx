import { Search } from "@/src/components/Search/Search";
import { Typography } from "@/src/components/Typography/Typography";
import Icon from "@/src/components/Icon/Icon";
import { Combobox } from "@kobalte/core/combobox";
import { css } from "@linaria/core";
import {
  Service,
  useClanContext,
  useServiceInstancesContext,
} from "@/src/models";
import { Component, Show } from "solid-js";
import { useUIContext } from "@/src/models/ui";
import { onClickOutside } from "@/src/util";

// TODO: Move this to typography styles
const tag = css`
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
`;

interface Module {
  value: string;
  label: string;
  raw: Service;
}

const SelectService: Component = () => {
  const [, { setToolbarMode }] = useUIContext();
  const [, { activateServiceInstance }] = useServiceInstancesContext();
  const [clan] = useClanContext();

  // https://docs.solidjs.com/reference/jsx-attributes/use#avoiding-tree-shaking
  /* eslint-disable no-constant-binary-expression, @typescript-eslint/no-unused-expressions */
  false && onClickOutside;

  return (
    <div
      use:onClickOutside={() => setToolbarMode({ type: "select" })}
      class="absolute bottom-full left-1/2 mb-2 -translate-x-1/2"
    >
      <div class="w-[30rem]">
        <Search<Module>
          height="13rem"
          onChange={(data) => {
            const service = data?.raw;
            if (!service) {
              return;
            }
            const instance = service.instances?.[0];
            if (instance) {
              activateServiceInstance(instance);
            } else {
              setToolbarMode({
                type: "service",
                service,
              });
            }
          }}
          options={clan().services.sorted.map((service) => ({
            value: `${service.id}:${service.source}`,
            label: service.id,
            raw: service,
          }))}
          renderItem={(item, opts) => {
            return (
              <div class="flex items-center justify-between gap-2 overflow-hidden rounded-md px-2 py-1 pr-4">
                <div class="flex size-8 shrink-0 items-center justify-center rounded-md bg-white">
                  <Icon icon="Code" />
                </div>
                <div class="flex w-full flex-col">
                  <Combobox.ItemLabel class="flex gap-1.5">
                    <Show when={item.raw.instances.length !== 0}>
                      <div class="flex items-center rounded bg-[#76FFA4] px-1 py-0.5">
                        <span class={tag}>Added</span>
                      </div>
                    </Show>
                    <Typography
                      hierarchy="body"
                      size="s"
                      weight="medium"
                      inverted
                    >
                      {item.label}
                    </Typography>
                  </Combobox.ItemLabel>
                  <Typography
                    hierarchy="body"
                    size="xxs"
                    weight="normal"
                    color="quaternary"
                    inverted
                    in="SelectService-item-description"
                  >
                    <span class="inline-block max-w-80 truncate align-middle">
                      {item.raw.description}
                    </span>
                    <span class="inline-block max-w-32 truncate align-middle">
                      <Show when={!item.raw.isCore} fallback="by clan-core">
                        by {item.raw.source}
                      </Show>
                    </span>
                  </Typography>
                </div>
              </div>
            );
          }}
        />
      </div>
    </div>
  );
};
export default SelectService;
