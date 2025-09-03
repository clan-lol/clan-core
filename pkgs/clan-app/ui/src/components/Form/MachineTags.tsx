import { Combobox } from "@kobalte/core/combobox";
import { FieldProps } from "./Field";
import {
  createEffect,
  on,
  createSignal,
  For,
  Show,
  splitProps,
} from "solid-js";
import Icon from "../Icon/Icon";
import cx from "classnames";
import { Typography } from "@/src/components/Typography/Typography";
import { Tag } from "@/src/components/Tag/Tag";

import { Label } from "@/src/components/Form/Label";
import { Orienter } from "@/src/components/Form/Orienter";
import { CollectionNode } from "@kobalte/core";
import styles from "./MachineTags.module.css";

export interface MachineTag {
  value: string;
  disabled?: boolean;
}

export type MachineTagsProps = FieldProps & {
  name: string;
  onChange: (values: string[]) => void;
  defaultValue?: string[];
  readOnly?: boolean;
  disabled?: boolean;
  required?: boolean;
  defaultOptions?: string[];
  readonlyOptions?: string[];
};

const uniqueOptions = (options: MachineTag[]) => {
  const record: Record<string, MachineTag> = {};
  options.forEach((option) => {
    // we want to preserve the first one we encounter
    // this allows us to prefix the default 'all' tag
    record[option.value] = record[option.value] || option;
  });
  return Object.values(record);
};

const sortedOptions = (options: MachineTag[]) =>
  options.sort((a, b) => a.value.localeCompare(b.value));

const sortedAndUniqueOptions = (options: MachineTag[]) =>
  sortedOptions(uniqueOptions(options));

export const MachineTags = (props: MachineTagsProps) => {
  const [local, rest] = splitProps(props, ["defaultValue"]);

  // // convert default value string[] into MachineTag[]
  const defaultValue = sortedAndUniqueOptions(
    (local.defaultValue || []).map((value) => ({ value })),
  );

  // convert default options string[] into MachineTag[]
  const [availableOptions, setAvailableOptions] = createSignal<MachineTag[]>(
    sortedAndUniqueOptions([
      ...(props.readonlyOptions || []).map((value) => ({
        value,
        disabled: true,
      })),
      ...(props.defaultOptions || []).map((value) => ({ value })),
    ]),
  );

  const [selectedOptions, setSelectedOptions] =
    createSignal<MachineTag[]>(defaultValue);

  const handleToggle = (item: CollectionNode<MachineTag>) => () => {
    setSelectedOptions((current) => {
      const exists = current.find(
        (option) => option.value === item.rawValue.value,
      );
      if (exists) {
        return current.filter((option) => option.value !== item.rawValue.value);
      }
      return [...current, item.rawValue];
    });
  };

  // customises how each option is displayed in the dropdown
  const ItemComponent =
    (inverted: boolean) => (props: { item: CollectionNode<MachineTag> }) => {
      return (
        <Combobox.Item
          item={props.item}
          class={cx(styles.listboxItem, {
            [styles.listboxItemInverted]: inverted,
          })}
          onClick={handleToggle(props.item)}
        >
          <Combobox.ItemLabel>
            <Typography
              hierarchy="body"
              size="xs"
              weight="bold"
              inverted={inverted}
            >
              {props.item.textValue}
            </Typography>
          </Combobox.ItemLabel>
          <Combobox.ItemIndicator class={styles.itemIndicator}>
            <Icon icon="Checkmark" inverted={inverted} />
          </Combobox.ItemIndicator>
        </Combobox.Item>
      );
    };

  let selectRef: HTMLSelectElement;

  const onKeyDown = (event: KeyboardEvent) => {
    // react when enter is pressed inside of the text input
    if (event.key === "Enter") {
      event.preventDefault();
      event.stopPropagation();

      // get the current input value, exiting early if it's empty
      const input = event.currentTarget as HTMLInputElement;
      const trimmed = input.value.trim();
      if (!trimmed) return;

      setAvailableOptions((curr) => {
        if (curr.find((option) => option.value === trimmed)) {
          return curr;
        }
        return [
          ...curr,
          {
            value: trimmed,
          },
        ];
      });
      setSelectedOptions((curr) => {
        if (curr.find((option) => option.value === trimmed)) {
          return curr;
        }
        return [
          ...curr,
          {
            value: trimmed,
          },
        ];
      });

      selectRef.dispatchEvent(
        new Event("input", { bubbles: true, cancelable: true }),
      );
      selectRef.dispatchEvent(
        new Event("change", { bubbles: true, cancelable: true }),
      );
      input.value = "";
    }
  };

  // Notify when selected options change
  createEffect(
    on(selectedOptions, (options) => {
      props.onChange(options.map((o) => o.value));
    }),
  );

  const align = () => {
    if (props.readOnly) {
      return "center";
    } else {
      return props.orientation === "horizontal" ? "start" : "center";
    }
  };

  return (
    <Combobox<MachineTag>
      multiple
      class={cx("form-field", styles.machineTags, props.orientation)}
      {...splitProps(props, ["defaultValue"])[1]}
      defaultValue={defaultValue}
      value={selectedOptions()}
      options={availableOptions()}
      optionValue="value"
      optionTextValue="value"
      optionLabel="value"
      optionDisabled="disabled"
      itemComponent={ItemComponent(props.inverted || false)}
      placeholder="Start typing a name and press enter"
      onChange={() => {
        // noop, we handle this via the selectedOptions signal
      }}
    >
      <Orienter orientation={props.orientation} align={align()}>
        <Label
          labelComponent={Combobox.Label}
          descriptionComponent={Combobox.Description}
          {...props}
        />

        <Combobox.HiddenSelect
          multiple
          ref={(el) => {
            selectRef = el;
          }}
        />

        <Combobox.Control<MachineTag>
          class={cx(styles.control, props.orientation)}
        >
          {(state) => (
            <div class={styles.selectedOptions}>
              <For each={state.selectedOptions()}>
                {(option) => (
                  <Tag
                    inverted={props.inverted}
                    interactive={
                      !(option.disabled || props.disabled || props.readOnly)
                    }
                    icon={({ inverted }) =>
                      option.disabled ||
                      props.disabled ||
                      props.readOnly ? undefined : (
                        <Icon
                          role="button"
                          icon={"Close"}
                          size="0.5rem"
                          inverted={inverted}
                          onClick={() =>
                            setSelectedOptions((curr) => {
                              return curr.filter(
                                (o) => o.value !== option.value,
                              );
                            })
                          }
                        />
                      )
                    }
                  >
                    {option.value}
                  </Tag>
                )}
              </For>
              <Show when={!props.readOnly}>
                <Combobox.Trigger class={styles.trigger}>
                  <Icon
                    icon="Tag"
                    color="secondary"
                    inverted={props.inverted}
                    class={cx(styles.icon, {
                      [styles.iconSmall]: props.size == "s",
                    })}
                  />
                  <Combobox.Input
                    onKeyDown={onKeyDown}
                    class={cx(styles.input, {
                      [styles.inputSmall]: props.size == "s",
                      [styles.inputGhost]: props.ghost,
                      [styles.inputInverted]: props.inverted,
                    })}
                  />
                </Combobox.Trigger>
              </Show>
            </div>
          )}
        </Combobox.Control>
      </Orienter>
      <Combobox.Portal>
        <Combobox.Content
          class={cx(styles.comboboxContent, {
            [styles.comboboxContentInverted]: props.inverted,
          })}
        >
          <Combobox.Listbox class={styles.listbox} />
        </Combobox.Content>
      </Combobox.Portal>
    </Combobox>
  );
};
