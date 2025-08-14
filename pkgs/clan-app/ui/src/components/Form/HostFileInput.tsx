import {
  TextField,
  TextFieldInputProps,
  TextFieldRootProps,
} from "@kobalte/core/text-field";

import cx from "classnames";
import { Label } from "./Label";
import { Button } from "../Button/Button";
import styles from "./HostFileInput.module.css";
import { PolymorphicProps } from "@kobalte/core/polymorphic";
import { FieldProps } from "./Field";
import { Orienter } from "./Orienter";
import { createSignal } from "solid-js";
import { Tooltip } from "@kobalte/core/tooltip";
import { Typography } from "@/src/components/Typography/Typography";

export type HostFileInputProps = FieldProps &
  TextFieldRootProps & {
    onSelectFile: () => Promise<string>;
    input?: PolymorphicProps<"input", TextFieldInputProps<"input">>;
    placeholder?: string;
  };

export const HostFileInput = (props: HostFileInputProps) => {
  const [value, setValue] = createSignal<string>(props.value || "");

  let actualInputElement: HTMLInputElement | undefined;

  const selectFile = async () => {
    try {
      console.log("selecting file", props.onSelectFile);
      setValue(await props.onSelectFile());
      actualInputElement?.dispatchEvent(
        new Event("input", { bubbles: true, cancelable: true }),
      );
    } catch (error) {
      console.log("Error selecting file", error);
      // todo work out how to display the error
    }
  };

  return (
    <TextField
      class={cx("form-field", props.size, props.orientation, {
        inverted: props.inverted,
        ghost: props.ghost,
      })}
      {...props}
    >
      <Orienter
        orientation={props.orientation}
        align={props.orientation == "horizontal" ? "center" : "start"}
      >
        <Label
          labelComponent={TextField.Label}
          descriptionComponent={TextField.Description}
          {...props}
        />

        <TextField.Input
          {...props.input}
          hidden={true}
          value={value()}
          ref={(el: HTMLInputElement) => {
            actualInputElement = el; // Capture for local use
          }}
        />

        {!value() && (
          <Button
            hierarchy="secondary"
            size={props.size}
            startIcon="Folder"
            onClick={selectFile}
            disabled={props.disabled || props.readOnly}
            class={cx(
              props.orientation === "vertical"
                ? styles.vertical_button
                : styles.horizontal_button,
            )}
          >
            {props.placeholder || "No Selection"}
          </Button>
        )}

        {value() && (
          <Tooltip placement="top">
            <Tooltip.Portal>
              <Tooltip.Content class="tooltip-content">
                <Typography
                  hierarchy="body"
                  size="xs"
                  weight="medium"
                  inverted={!props.inverted}
                >
                  {value()}
                </Typography>
                <Tooltip.Arrow />
              </Tooltip.Content>
            </Tooltip.Portal>
            <Tooltip.Trigger
              as={Button}
              class={cx(
                props.orientation === "vertical"
                  ? styles.vertical_button
                  : styles.horizontal_button,
              )}
              hierarchy="secondary"
              size={props.size}
              startIcon="Folder"
              onClick={selectFile}
              disabled={props.disabled || props.readOnly}
            >
              {value()}
            </Tooltip.Trigger>
          </Tooltip>
        )}
      </Orienter>
    </TextField>
  );
};
