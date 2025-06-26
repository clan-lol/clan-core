import {
  TextField as KTextField,
  TextFieldInputProps as KTextFieldInputProps,
  TextFieldTextAreaProps as KTextFieldTextAreaProps,
} from "@kobalte/core/text-field";
import {
  Checkbox as KCheckbox,
  CheckboxInputProps as KCheckboxInputProps,
} from "@kobalte/core/checkbox";
import { Typography } from "@/src/components/v2/Typography/Typography";
import Icon, { IconVariant } from "@/src/components/v2/Icon/Icon";

import cx from "classnames";
import { Match, splitProps, Switch } from "solid-js";
import { Dynamic } from "solid-js/web";
import { Tooltip as KTooltip } from "@kobalte/core/tooltip";
import "./Field.css";

type Size = "default" | "s";
export type Orientation = "horizontal" | "vertical";
type FieldType = "text" | "textarea" | "checkbox";

export interface TextFieldProps {
  input?: KTextFieldInputProps;
  value?: string;
  onChange?: (value: string) => void;
  defaultValue?: string;
}

export interface TextAreaProps {
  input?: KTextFieldTextAreaProps;
  value?: string;
  onChange?: (value: string) => void;
  defaultValue?: string;
}

export interface CheckboxProps {
  input?: KCheckboxInputProps;
  checked?: boolean;
  defaultChecked?: boolean;
  indeterminate?: boolean;
  onChange?: (value: boolean) => void;
}

export interface FieldProps {
  class?: string;
  name?: string;
  label?: string;
  description?: string;
  tooltip?: string;
  icon?: IconVariant;
  ghost?: boolean;

  size?: Size;
  orientation?: Orientation;
  inverted?: boolean;

  required?: boolean;
  disabled?: boolean;
  readOnly?: boolean;
  invalid?: boolean;

  type: FieldType;
  text?: TextFieldProps;
  textarea?: TextAreaProps;
  checkbox?: CheckboxProps;
}

const componentsForType = {
  text: {
    container: KTextField,
    label: KTextField.Label,
    description: KTextField.Description,
  },
  textarea: {
    container: KTextField,
    label: KTextField.Label,
    description: KTextField.Description,
  },
  checkbox: {
    container: KCheckbox,
    label: KCheckbox.Label,
    description: KCheckbox.Description,
  },
};

export const Field = (props: FieldProps) => {
  const [commonProps] = splitProps(props, [
    "name",
    "class",
    "required",
    "disabled",
    "readOnly",
  ]);

  const [textProps] = splitProps(props.text || props.textarea || {}, [
    "value",
    "onChange",
    "defaultValue",
  ]);

  const [checkboxProps] = splitProps(props.checkbox || {}, [
    "checked",
    "defaultChecked",
    "indeterminate",
  ]);

  const validationState = () => (props.invalid ? "invalid" : "valid");

  const labelSize = () => `size-${props.size || "default"}`;
  const orientation = () => `orientation-${props.orientation || "vertical"}`;
  const descriptionSize = () => (labelSize() == "size-default" ? "xs" : "xxs");
  const fieldClass = () => (props.type ? `form-field-${props.type}` : "");

  const { container, label, description } = componentsForType[props.type];

  return (
    <Dynamic
      component={container}
      class={cx("form-field", fieldClass(), labelSize(), orientation(), {
        inverted: props.inverted,
        ghost: props.ghost,
      })}
      validationState={validationState()}
      {...commonProps}
      {...textProps}
      {...checkboxProps}
    >
      {props.label && (
        <div class="meta">
          {props.label && (
            <Dynamic component={label}>
              <Typography
                hierarchy="label"
                size={props.size || "default"}
                color={props.invalid ? "error" : "primary"}
                weight="bold"
                inverted={props.inverted}
              >
                {props.label}
              </Typography>

              {props.tooltip && (
                <KTooltip>
                  <KTooltip.Trigger class="tooltip-trigger">
                    <Icon
                      icon="Info"
                      color="tertiary"
                      inverted={props.inverted}
                      size={props.size == "default" ? "0.85em" : "0.75rem"}
                    />
                    <KTooltip.Portal>
                      <KTooltip.Content>
                        <Typography hierarchy="body" size="xs">
                          {props.tooltip}
                        </Typography>
                      </KTooltip.Content>
                    </KTooltip.Portal>
                  </KTooltip.Trigger>
                </KTooltip>
              )}
            </Dynamic>
          )}
          {props.description && (
            <Dynamic component={description}>
              <Typography
                hierarchy="body"
                size={descriptionSize()}
                color="secondary"
                weight="normal"
                inverted={props.inverted}
              >
                {props.description}
              </Typography>
            </Dynamic>
          )}
        </div>
      )}

      <Switch>
        <Match when={props.type == "text"}>
          <div class="input-container">
            {props.icon && (
              <Icon
                icon={props.icon}
                inverted={props.inverted}
                color={props.disabled ? "quaternary" : "tertiary"}
              />
            )}
            <KTextField.Input
              {...props.text?.input}
              classList={{ "has-icon": props.icon }}
            />
          </div>
        </Match>
        <Match when={props.type == "textarea"}>
          <KTextField.TextArea {...props.textarea?.input} />
        </Match>
        <Match when={props.type == "checkbox"}>
          <KCheckbox.Input {...props.checkbox?.input} />
          <KCheckbox.Control class="checkbox-control">
            <KCheckbox.Indicator>
              <Icon
                icon="Checkmark"
                inverted={props.inverted}
                color="secondary"
              />
            </KCheckbox.Indicator>
          </KCheckbox.Control>
        </Match>
      </Switch>
    </Dynamic>
  );
};
