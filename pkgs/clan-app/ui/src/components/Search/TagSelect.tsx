import Icon from "../Icon/Icon";
import { Typography } from "../Typography/Typography";
import { For, JSX, Show } from "solid-js";
import styles from "./TagSelect.module.css";
import { Combobox } from "@kobalte/core/combobox";
import { Button } from "../Button/Button";

// Base props common to both modes
export interface TagSelectProps<T> {
  onClick: () => void;
  label: string;
  values: T[];
  options: T[];
  renderItem: (item: T) => JSX.Element;
}

/**
 * Shallowly interactive field for selecting multiple tags / machines.
 * It does only handle click and focus interactions
 * Displays the selected items as tags
 */
export function TagSelect<T extends { value: unknown }>(
  props: TagSelectProps<T>,
) {
  const optionValue = "value";
  return (
    <div class="flex flex-col gap-1.5">
      <div class="flex w-full items-center gap-2 px-1.5 py-0">
        <Typography
          hierarchy="label"
          weight="medium"
          size="xs"
          inverted
          color="secondary"
          transform="uppercase"
          in="TagSelect-label"
        >
          {props.label}
        </Typography>
        <Icon icon="Info" color="tertiary" inverted size={11} />
        <Button
          icon="Settings"
          hierarchy="primary"
          ghost
          size="xs"
          in="TagSelect"
        />
      </div>
      <Combobox<T>
        multiple
        optionValue={optionValue}
        value={props.values}
        options={props.options}
        allowsEmptyCollection
        class="w-full"
      >
        <Combobox.Control<T> aria-label="Fruits">
          {(state) => {
            return (
              <Combobox.Trigger
                tabIndex={1}
                class={styles.trigger}
                onClick={props.onClick}
              >
                <div class="flex flex-wrap items-center gap-2 px-2 py-3">
                  <Icon icon="Search" color="quaternary" inverted />
                  <Show when={state.selectedOptions().length === 0}>
                    <Typography
                      color="tertiary"
                      inverted
                      hierarchy="body"
                      size="s"
                    >
                      Select
                    </Typography>
                  </Show>
                  <For each={state.selectedOptions()}>{props.renderItem}</For>
                </div>
              </Combobox.Trigger>
            );
          }}
        </Combobox.Control>
      </Combobox>
    </div>
  );
}
