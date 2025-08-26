import Icon from "../Icon/Icon";
import { Typography } from "../Typography/Typography";
import { For, JSX, Show } from "solid-js";
import styles from "./TagSelect.module.css";
import { Combobox } from "@kobalte/core/combobox";
import { Button } from "../Button/Button";

export interface TagSelectProps<T> {
  // Define any props needed for the SelectStepper component
  values: T[];
  options: T[];
  onChange: (values: T[]) => void;
  onClick: () => void;
  renderItem: (item: T) => JSX.Element;
}

export function TagSelect<T>(props: TagSelectProps<T>) {
  return (
    <div class={styles.dummybg}>
      <div class="flex flex-col gap-1.5">
        <div class="flex w-full items-center gap-2 px-1.5">
          <Typography
            hierarchy="body"
            weight="medium"
            class="flex gap-2 uppercase"
            size="s"
            inverted
            color="secondary"
          >
            Servers
          </Typography>
          <Icon icon="Info" color="tertiary" inverted />
          <Button icon="Settings" hierarchy="primary" ghost class="ml-auto" />
        </div>
        <Combobox<T>
          multiple
          value={props.values}
          onChange={props.onChange}
          options={props.options}
          allowsEmptyCollection
          class="w-full"
        >
          <Combobox.Control<T> aria-label="Fruits">
            {(state) => (
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
            )}
          </Combobox.Control>
        </Combobox>
      </div>
    </div>
  );
}
