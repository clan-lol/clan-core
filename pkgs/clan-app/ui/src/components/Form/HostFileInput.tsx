import { TextField } from "@kobalte/core/text-field";

import cx from "classnames";
import { Label } from "./Label";
import { Button } from "../Button/Button";
import styles from "./HostFileInput.module.css";
import { FieldProps } from "./Field";
import { Orienter } from "./Orienter";
import { createSignal, JSX, splitProps } from "solid-js";
import { Tooltip } from "@kobalte/core/tooltip";
import { Typography } from "@/src/components/Typography/Typography";
import { keepTruthy } from "@/src/util";
import { useSysContext } from "@/src/models";

export type HostFileInputProps = FieldProps & {
  name: string;
  windowTitle?: string;
  required?: boolean;
  disabled?: boolean;
  placeholder?: string;
  initialFolder?: string;
  readOnly?: boolean;
  defaultValue?: string;
  ref?: (element: HTMLInputElement) => void;
  onInput?: JSX.EventHandler<
    HTMLInputElement | HTMLTextAreaElement,
    InputEvent
  >;
  onChange?: JSX.EventHandler<HTMLInputElement | HTMLTextAreaElement, Event>;
  onBlur?: JSX.EventHandler<HTMLInputElement | HTMLTextAreaElement, FocusEvent>;
};

export const HostFileInput = (props: HostFileInputProps) => {
  const [, { pickDir }] = useSysContext();
  const [rootProps, inputProps, local, labelProps] = splitProps(
    props,
    ["name", "defaultValue", "required", "disabled"],
    ["onInput", "onChange", "onBlur"],
    ["windowTitle", "initialFolder", "readOnly", "ref", "placeholder"],
  );

  let inputElement!: HTMLInputElement;
  const [value, setValue] = createSignal(rootProps.defaultValue || "");

  const onSelectFile = async () => {
    if (local.readOnly) {
      return;
    }

    // TOOD: When a user clicks cancel button in the file picker, an error will
    // be return, the backend should provide more data so we can target the
    // cancellation specifically and not swallow other errors
    const path = await pickDir({
      title: local.windowTitle || labelProps.label,
      initialPath: local.initialFolder,
    });

    setValue(path);
    inputElement.dispatchEvent(
      new Event("input", { bubbles: true, cancelable: true }),
    );
  };

  return (
    <TextField {...rootProps} value={value()}>
      <Orienter
        orientation={labelProps.orientation}
        align={labelProps.orientation == "horizontal" ? "center" : "start"}
      >
        <Label
          {...labelProps}
          labelComponent={TextField.Label}
          descriptionComponent={TextField.Description}
          in={keepTruthy(
            labelProps.orientation == "horizontal" && "Orienter-horizontal",
          )}
        />

        <TextField.Input
          {...inputProps}
          hidden={true}
          ref={(el: HTMLInputElement) => {
            inputElement = el;
            local.ref?.(el);
          }}
        />

        {!value() && (
          <Button
            hierarchy="secondary"
            size={labelProps.size}
            icon="Folder"
            onClick={onSelectFile}
            disabled={rootProps.disabled || local.readOnly}
            elasticity={
              labelProps.orientation === "vertical" ? "fit" : undefined
            }
            in={
              labelProps.orientation == "horizontal"
                ? `HostFileInput-${labelProps.orientation}`
                : undefined
            }
          >
            {local.placeholder || "No Selection"}
          </Button>
        )}

        {value() && (
          <Tooltip placement="top">
            <Tooltip.Portal>
              <Tooltip.Content
                class={cx(styles.tooltipContent, {
                  [styles.inverted]: labelProps.inverted,
                })}
              >
                <Typography
                  hierarchy="body"
                  size="xs"
                  weight="medium"
                  inverted={!labelProps.inverted}
                >
                  {value()}
                </Typography>
                <Tooltip.Arrow />
              </Tooltip.Content>
            </Tooltip.Portal>
            <Tooltip.Trigger
              as={Button}
              elasticity={
                labelProps.orientation === "vertical" ? "fit" : undefined
              }
              in={
                labelProps.orientation == "horizontal"
                  ? `HostFileInput-${labelProps.orientation}`
                  : undefined
              }
              hierarchy="secondary"
              size={labelProps.size}
              icon="Folder"
              onClick={onSelectFile}
              disabled={rootProps.disabled || local.readOnly}
            >
              {value()}
            </Tooltip.Trigger>
          </Tooltip>
        )}
      </Orienter>
    </TextField>
  );
};
