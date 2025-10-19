import { Search } from "@/src/components/Search/Search";
import { Typography } from "@/src/components/Typography/Typography";
import { buildServicePath, useClanURI } from "@/src/hooks/clan";
import { useServiceInstances, useServiceModules } from "@/src/hooks/queries";
import { useNavigate } from "@solidjs/router";
import { createEffect, createSignal, Show } from "solid-js";
import { Module } from "./models";
import Icon from "@/src/components/Icon/Icon";
import { Combobox } from "@kobalte/core/combobox";
import { useClickOutside } from "@/src/hooks/useClickOutside";
import { css } from "@linaria/core";

// TODO: Move this to typography styles
const tag = css`
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
`;

interface FlyoutProps {
  onClose: () => void;
}
export const SelectService = (props: FlyoutProps) => {
  const clanURI = useClanURI();

  const serviceModulesQuery = useServiceModules(clanURI);
  const serviceInstancesQuery = useServiceInstances(clanURI);

  const [moduleOptions, setModuleOptions] = createSignal<Module[]>([]);

  createEffect(() => {
    if (serviceModulesQuery.data && serviceInstancesQuery.data) {
      setModuleOptions(
        serviceModulesQuery.data.modules.map((currService) => ({
          value: `${currService.usage_ref.name}:${currService.usage_ref.input}`,
          label: currService.usage_ref.name,
          raw: currService,
        })),
      );
    }
  });

  const handleChange = (module: Module | null) => {
    if (!module) return;

    const serviceURL = buildServicePath({
      clanURI,
      id: module.raw.instance_refs[0] || module.raw.usage_ref.name,
      module: {
        name: module.raw.usage_ref.name,
        input: module.raw.usage_ref.input,
      },
    });
    navigate(serviceURL);
  };
  const navigate = useNavigate();

  let ref: HTMLDivElement;

  useClickOutside(
    () => ref,
    () => {
      props.onClose();
    },
  );
  return (
    <div
      ref={(e) => (ref = e)}
      class="absolute bottom-full left-1/2 mb-2 -translate-x-1/2"
    >
      <div class="w-[30rem]">
        <Search<Module>
          loading={
            serviceModulesQuery.isLoading || serviceInstancesQuery.isLoading
          }
          height="13rem"
          onChange={handleChange}
          options={moduleOptions()}
          renderItem={(item, opts) => {
            return (
              <div class="flex items-center justify-between gap-2 overflow-hidden rounded-md px-2 py-1 pr-4">
                <div class="flex size-8 shrink-0 items-center justify-center rounded-md bg-white">
                  <Icon icon="Code" />
                </div>
                <div class="flex w-full flex-col">
                  <Combobox.ItemLabel class="flex gap-1.5">
                    <Show when={item.raw.instance_refs.length > 0}>
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
                      {item.raw.info.manifest.description}
                    </span>
                    <span class="inline-block max-w-32 truncate align-middle">
                      <Show when={!item.raw.native} fallback="by clan-core">
                        by {item.raw.usage_ref.input}
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
