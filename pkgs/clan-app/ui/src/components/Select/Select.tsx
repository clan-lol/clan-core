import { Select as KSelect } from "@kobalte/core/select";
import Icon from "../Icon/Icon";
import { Orienter } from "../Form/Orienter";
import { Label, LabelProps } from "../Form/Label";
import { createEffect, createSignal, JSX, splitProps } from "solid-js";
import styles from "./Select.module.css";
import { Typography } from "../Typography/Typography";
import cx from "classnames";

export interface Option { value: string; label: string; disabled?: boolean }

export interface SelectProps {
  // Kobalte Select props, for modular forms
  name: string;
  placeholder?: string | undefined;
  options: Option[];
  value: string | undefined;
  error: string;
  required?: boolean | undefined;
  disabled?: boolean | undefined;
  ref: (element: HTMLSelectElement) => void;
  onInput: JSX.EventHandler<HTMLSelectElement, InputEvent>;
  onChange: JSX.EventHandler<HTMLSelectElement, Event>;
  onBlur: JSX.EventHandler<HTMLSelectElement, FocusEvent>;
  // Custom props
  orientation?: "horizontal" | "vertical";
  label?: Omit<LabelProps, "labelComponent" | "descriptionComponent">;
}

export const Select = (props: SelectProps) => {
  const [root, selectProps] = splitProps(
    props,
    ["name", "placeholder", "options", "required", "disabled"],
    ["placeholder", "ref", "onInput", "onChange", "onBlur"],
  );

  const [getValue, setValue] = createSignal<Option>();

  createEffect(() => {
    setValue(props.options.find((option) => props.value === option.value));
  });

  return (
    <KSelect
      {...root}
      sameWidth={true}
      gutter={0}
      multiple={false}
      value={getValue()}
      onChange={setValue}
      optionValue="value"
      optionTextValue="label"
      optionDisabled="disabled"
      validationState={props.error ? "invalid" : "valid"}
      itemComponent={(props) => (
        <KSelect.Item item={props.item} class="flex gap-1 p-2">
          <KSelect.ItemIndicator>
            <Icon icon="Checkmark" />
          </KSelect.ItemIndicator>
          <KSelect.ItemLabel>
            <Typography
              hierarchy="body"
              size="xs"
              weight="bold"
              class="flex w-full items-center"
            >
              {props.item.rawValue.label}
            </Typography>
          </KSelect.ItemLabel>
        </KSelect.Item>
      )}
      placeholder={
        <Typography
          hierarchy="body"
          size="xs"
          weight="bold"
          class="flex w-full items-center"
        >
          {props.placeholder}
        </Typography>
      }
    >
      <Orienter orientation={props.orientation || "horizontal"}>
        <Label
          {...props.label}
          labelComponent={KSelect.Label}
          descriptionComponent={KSelect.Description}
          validationState={props.error ? "invalid" : "valid"}
        />
        <KSelect.HiddenSelect {...selectProps} />
        <KSelect.Trigger class={cx(styles.trigger)}>
          <KSelect.Value<Option>>
            {(state) => (
              <Typography
                hierarchy="body"
                size="xs"
                weight="bold"
                class="flex w-full items-center"
              >
                {state.selectedOption().label}
              </Typography>
            )}
          </KSelect.Value>
          <KSelect.Icon as="button" class={styles.icon}>
            <Icon icon="Expand" color="inherit" />
          </KSelect.Icon>
        </KSelect.Trigger>
      </Orienter>
      <KSelect.Portal>
        <KSelect.Content class={styles.options_content}>
          <KSelect.Listbox />
        </KSelect.Content>
      </KSelect.Portal>
      {/* TODO: Display error next to the problem */}
      {/* <KSelect.ErrorMessage>{props.error}</KSelect.ErrorMessage> */}
    </KSelect>
  );
};
