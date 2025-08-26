import { Combobox } from "@kobalte/core/combobox";
import { FieldProps } from "./Field";
import { ComponentProps, createSignal, For, Show, splitProps } from "solid-js";
import Icon from "../Icon/Icon";
import cx from "classnames";
import { Typography } from "@/src/components/Typography/Typography";
import { Tag } from "@/src/components/Tag/Tag";

import "./MachineTags.css";
import { Label } from "@/src/components/Form/Label";
import { Orienter } from "@/src/components/Form/Orienter";
import { CollectionNode } from "@kobalte/core";

export interface MachineTag {
  value: string;
  disabled?: boolean;
  new?: boolean;
}

export type MachineTagsProps = FieldProps & {
  name: string;
  input: ComponentProps<"select">;
  readOnly?: boolean;
  disabled?: boolean;
  required?: boolean;
  defaultValue?: string[];
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

// customises how each option is displayed in the dropdown
const ItemComponent = (props: { item: CollectionNode<MachineTag> }) => {
  return (
    <Combobox.Item item={props.item} class="item">
      <Combobox.ItemLabel>
        <Typography hierarchy="body" size="xs" weight="bold">
          {props.item.textValue}
        </Typography>
      </Combobox.ItemLabel>
      <Combobox.ItemIndicator class="item-indicator">
        <Icon icon="Checkmark" />
      </Combobox.ItemIndicator>
    </Combobox.Item>
  );
};

export const MachineTags = (props: MachineTagsProps) => {
  // convert default value string[] into MachineTag[]
  const defaultValue = sortedAndUniqueOptions(
    (props.defaultValue || []).map((value) => ({ value })),
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

  const onKeyDown = (event: KeyboardEvent) => {
    // react when enter is pressed inside of the text input
    if (event.key === "Enter") {
      event.preventDefault();
      event.stopPropagation();

      // get the current input value, exiting early if it's empty
      const input = event.currentTarget as HTMLInputElement;
      if (input.value === "") return;

      setAvailableOptions((options) => {
        return options.map((option) => {
          return {
            ...option,
            new: undefined,
          };
        });
      });

      // reset the input value
      input.value = "";
    }
  };

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
      class={cx("form-field", "machine-tags", props.size, props.orientation, {
        inverted: props.inverted,
        ghost: props.ghost,
      })}
      {...splitProps(props, ["defaultValue"])[1]}
      defaultValue={defaultValue}
      options={availableOptions()}
      optionValue="value"
      optionTextValue="value"
      optionLabel="value"
      optionDisabled="disabled"
      itemComponent={ItemComponent}
      placeholder="Enter a tag name"
      // triggerMode="focus"
      removeOnBackspace={false}
      defaultFilter={() => true}
      onInput={(event) => {
        const input = event.target as HTMLInputElement;

        // as the user types in the input box, we maintain a "new" option
        // in the list of available options
        setAvailableOptions((options) => {
          return [
            // remove the old "new" entry
            ...options.filter((option) => !option.new),
            // add the updated "new" entry
            { value: input.value, new: true },
          ];
        });
      }}
      onBlur={() => {
        // clear the in-progress "new" option from the list of available options
        setAvailableOptions((options) => {
          return options.filter((option) => !option.new);
        });
      }}
    >
      <Orienter orientation={props.orientation} align={align()}>
        <Label
          labelComponent={Combobox.Label}
          descriptionComponent={Combobox.Description}
          {...props}
        />

        <Combobox.HiddenSelect {...props.input} multiple />

        <Combobox.Control<MachineTag> class="control">
          {(state) => (
            <div class="selected-options">
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
                          onClick={() => state.remove(option)}
                        />
                      )
                    }
                  >
                    {option.value}
                  </Tag>
                )}
              </For>
              <Show when={!props.readOnly}>
                <div class="input-container">
                  <Combobox.Input onKeyDown={onKeyDown} />
                  <Combobox.Trigger class="trigger">
                    <Combobox.Icon class="icon">
                      <Icon
                        icon="Expand"
                        inverted={!props.inverted}
                        size="100%"
                      />
                    </Combobox.Icon>
                  </Combobox.Trigger>
                </div>
              </Show>
            </div>
          )}
        </Combobox.Control>
      </Orienter>

      <Combobox.Portal>
        <Combobox.Content class="machine-tags-content">
          <Combobox.Listbox class="listbox" />
        </Combobox.Content>
      </Combobox.Portal>
    </Combobox>
  );
};
