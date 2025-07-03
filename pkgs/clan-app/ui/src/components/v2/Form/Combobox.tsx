import Icon from "@/src/components/v2/Icon/Icon";
import {
  Combobox as KCombobox,
  ComboboxRootOptions as KComboboxRootOptions,
} from "@kobalte/core/combobox";
import { isFunction } from "@kobalte/utils";

import "./Combobox.css";
import { CollectionNode } from "@kobalte/core";
import { Label } from "./Label";
import cx from "classnames";
import { FieldProps } from "./Field";
import { Orienter } from "./Orienter";
import { Typography } from "@/src/components/v2/Typography/Typography";
import { Accessor, Component, For, Show, splitProps } from "solid-js";
import { Tag } from "@/src/components/v2/Tag/Tag";

export type ComboboxProps<Option, OptGroup = never> = FieldProps &
  KComboboxRootOptions<Option, OptGroup> & {
    inverted: boolean;
    itemControl?: Component<ComboboxControlState<Option>>;
  };

export const DefaultItemComponent = <Option,>(
  props: ComboboxItemComponentProps<Option>,
) => {
  return (
    <ComboboxItem item={props.item} class="item">
      <ComboboxItemLabel>
        <Typography hierarchy="body" size="xs" weight="bold">
          {props.item.textValue}
        </Typography>
      </ComboboxItemLabel>
      <ComboboxItemIndicator class="item-indicator">
        <Icon icon="Checkmark" />
      </ComboboxItemIndicator>
    </ComboboxItem>
  );
};

// adapted from https://github.com/kobaltedev/kobalte/blob/98a4810903c0c425d28cef4f0d1984192a225788/packages/core/src/combobox/combobox-base.tsx#L439
const getOptionTextValue = <Option,>(
  option: Option,
  optionTextValue:
    | keyof Exclude<Option, null>
    | ((option: Exclude<Option, null>) => string)
    | undefined,
) => {
  if (optionTextValue == null) {
    // If no `optionTextValue`, the option itself is the label (ex: string[] of options).
    return String(option);
  }

  // Get the label from the option object as a string.
  return String(
    isFunction(optionTextValue)
      ? optionTextValue(option as never)
      : (option as never)[optionTextValue],
  );
};

export const DefaultItemControl = <Option,>(
  props: ComboboxControlState<Option>,
) => (
  <>
    <Show when={props.multiple}>
      <div class="selected-options">
        <For each={props.selectedOptions()}>
          {(option) => (
            <Tag
              inverted={props.inverted}
              label={getOptionTextValue<Option>(option, props.optionTextValue)}
              action={
                props.disabled || props.readOnly
                  ? undefined
                  : {
                      icon: "Close",
                      onClick: () => props.remove(option),
                    }
              }
            />
          )}
        </For>
      </div>
    </Show>
    <div class="input-container">
      <KCombobox.Input />
      <KCombobox.Trigger class="trigger">
        <KCombobox.Icon class="icon">
          <Icon icon="Expand" inverted={props.inverted} size="100%" />
        </KCombobox.Icon>
      </KCombobox.Trigger>
    </div>
  </>
);

// todo aria-label on combobox.control and combobox.input
export const Combobox = <Option, OptGroup = never>(
  props: ComboboxProps<Option, OptGroup>,
) => {
  const itemControl = () => props.itemControl || DefaultItemControl;
  const itemComponent = () => props.itemComponent || DefaultItemComponent;

  const align = () => (props.orientation === "horizontal" ? "start" : "center");

  return (
    <KCombobox
      class={cx("form-field", "combobox", props.size, props.orientation, {
        inverted: props.inverted,
        ghost: props.ghost,
      })}
      {...props}
      itemComponent={itemComponent()}
    >
      <Orienter orientation={props.orientation} align={align()}>
        <Label
          labelComponent={KCombobox.Label}
          descriptionComponent={KCombobox.Description}
          {...props}
        />

        <KCombobox.Control<Option> class="control">
          {(state) => {
            const [controlProps] = splitProps(props, [
              "inverted",
              "multiple",
              "readOnly",
              "disabled",
            ]);
            return itemControl()({ ...state, ...controlProps });
          }}
        </KCombobox.Control>

        <KCombobox.Portal>
          <KCombobox.Content class="combobox-content">
            <KCombobox.Listbox class="listbox" />
          </KCombobox.Content>
        </KCombobox.Portal>
      </Orienter>
    </KCombobox>
  );
};

// todo can we replicate the . notation that Kobalte achieves with their type definitions?
export const ComboboxItem = KCombobox.Item;
export const ComboboxItemDescription = KCombobox.ItemDescription;
export const ComboboxItemIndicator = KCombobox.ItemIndicator;
export const ComboboxItemLabel = KCombobox.ItemLabel;

// these interfaces were not exported, so we re-declare them
export interface ComboboxItemComponentProps<Option> {
  /** The item to render. */
  item: CollectionNode<Option>;
}

export interface ComboboxSectionComponentProps<OptGroup> {
  /** The section to render. */
  section: CollectionNode<OptGroup>;
}

type ComboboxControlState<Option> = Pick<
  ComboboxProps<Option>,
  "optionTextValue" | "inverted" | "multiple" | "size" | "readOnly" | "disabled"
> & {
  /** The selected options. */
  selectedOptions: Accessor<Option[]>;
  /** A function to remove an option from the selection. */
  remove: (option: Option) => void;
  /** A function to clear the selection. */
  clear: () => void;
};
