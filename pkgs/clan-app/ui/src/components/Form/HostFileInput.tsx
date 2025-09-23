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
import { createSignal, mergeProps, splitProps } from "solid-js";
import { Tooltip } from "@kobalte/core/tooltip";
import { Typography } from "@/src/components/Typography/Typography";
import { keepTruthy } from "@/src/util";

export type HostFileInputProps = FieldProps &
  TextFieldRootProps & {
    onSelectFile: () => Promise<string>;
    input?: PolymorphicProps<"input", TextFieldInputProps<"input">>;
    placeholder?: string;
  };

export const HostFileInput = (props: HostFileInputProps) => {
  const withDefaults = mergeProps({ value: "" } as const, props);
  const [local, other] = splitProps(withDefaults, [
    "size",
    "orientation",
    "inverted",
    "ghost",
  ]);
  const [value, setValue] = createSignal<string>(other.value);

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
    <TextField {...other}>
      <Orienter
        orientation={local.orientation}
        align={local.orientation == "horizontal" ? "center" : "start"}
      >
        <Label
          labelComponent={TextField.Label}
          descriptionComponent={TextField.Description}
          in={keepTruthy(
            local.orientation == "horizontal" && "Orienter-horizontal",
          )}
          {...withDefaults}
        />

        <TextField.Input
          hidden={true}
          value={value()}
          ref={(el: HTMLInputElement) => {
            actualInputElement = el; // Capture for local use
          }}
          {...props.input}
        />

        {!value() && (
          <Button
            hierarchy="secondary"
            size={local.size}
            icon="Folder"
            onClick={selectFile}
            disabled={other.disabled || other.readOnly}
            elasticity={local.orientation === "vertical" ? "fit" : undefined}
            in={
              local.orientation == "horizontal"
                ? `HostFileInput-${local.orientation}`
                : undefined
            }
          >
            {props.placeholder || "No Selection"}
          </Button>
        )}

        {value() && (
          <Tooltip placement="top">
            <Tooltip.Portal>
              <Tooltip.Content
                class={cx(styles.tooltipContent, {
                  [styles.inverted]: local.inverted,
                })}
              >
                <Typography
                  hierarchy="body"
                  size="xs"
                  weight="medium"
                  inverted={!local.inverted}
                >
                  {value()}
                </Typography>
                <Tooltip.Arrow />
              </Tooltip.Content>
            </Tooltip.Portal>
            <Tooltip.Trigger
              as={Button}
              elasticity={local.orientation === "vertical" ? "fit" : undefined}
              in={
                local.orientation == "horizontal"
                  ? `HostFileInput-${local.orientation}`
                  : undefined
              }
              hierarchy="secondary"
              size={local.size}
              icon="Folder"
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
