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
import { createSignal, splitProps } from "solid-js";
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

  const [styleProps, otherProps] = splitProps(props, [
    "class",
    "size",
    "orientation",
    "inverted",
    "ghost",
  ]);

  return (
    <TextField
      class={cx(
        styleProps.class,
        "form-field",
        styleProps.size,
        styleProps.orientation,
        {
          inverted: styleProps.inverted,
          ghost: styleProps.ghost,
        },
      )}
      {...otherProps}
    >
      <Orienter
        orientation={styleProps.orientation}
        align={styleProps.orientation == "horizontal" ? "center" : "start"}
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
            size={styleProps.size}
            startIcon="Folder"
            onClick={selectFile}
            disabled={props.disabled || props.readOnly}
            class={cx(
              styleProps.orientation === "vertical"
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
              <Tooltip.Content class={styles.tooltipContent}>
                <Typography
                  hierarchy="body"
                  size="xs"
                  weight="medium"
                  inverted={!styleProps.inverted}
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
              size={styleProps.size}
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
