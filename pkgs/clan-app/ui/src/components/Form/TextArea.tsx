import {
  TextField,
  TextFieldRootProps,
  TextFieldTextAreaProps,
} from "@kobalte/core/text-field";

import cx from "classnames";
import { Label } from "./Label";
import { PolymorphicProps } from "@kobalte/core/polymorphic";
import { createEffect, createSignal, mergeProps, splitProps } from "solid-js";

import styles from "./TextField.module.css";
import { FieldProps } from "./Field";
import { Orienter } from "./Orienter";
import { keepTruthy } from "@/src/util";

export type TextAreaProps = FieldProps &
  TextFieldRootProps & {
    input: PolymorphicProps<"textarea", TextFieldTextAreaProps<"input">>;
    autoResize?: boolean;
    minRows?: number;
    maxRows?: number;
  };

export const TextArea = (props: TextAreaProps) => {
  const withDefaults = mergeProps(
    { size: "default", minRows: 1, maxRows: Infinity } as const,
    props,
  );
  const [local, other] = splitProps(withDefaults, [
    "autoResize",
    "minRows",
    "maxRows",
    "size",
    "orientation",
    "inverted",
    "ghost",
    "input",
  ]);

  let textareaRef: HTMLTextAreaElement;

  const [lineHeight, setLineHeight] = createSignal(0);

  const autoResize = () => {
    if (!(textareaRef && local.autoResize && lineHeight() > 0)) return;

    // Reset height to auto to get accurate scrollHeight
    textareaRef.style.height = "auto";

    // Calculate min and max heights based on rows
    const minHeight = local.minRows * lineHeight();
    const maxHeight = local.maxRows * lineHeight();

    // Set the height based on content, respecting min/max
    const newHeight = Math.min(
      Math.max(textareaRef.scrollHeight, minHeight),
      maxHeight,
    );

    // Update the height
    textareaRef.style.height = `${newHeight}px`;
    textareaRef.style.maxHeight = `${maxHeight}px`;
  };

  // Set up auto-resize effect
  createEffect(() => {
    if (textareaRef && local.autoResize) {
      // Get computed line height
      const computedStyle = window.getComputedStyle(textareaRef);
      const computedLineHeight = parseFloat(computedStyle.lineHeight);
      if (!isNaN(computedLineHeight)) {
        setLineHeight(computedLineHeight);
      }

      // Initial resize
      autoResize();
    }
  });

  // Watch for value changes to trigger resize
  createEffect(() => {
    if (local.autoResize && textareaRef) {
      // Access the value to create a dependency
      const _ = other.value || other.defaultValue;
      // Trigger resize on the next tick to ensure DOM is updated
      setTimeout(autoResize, 0);
    }
  });

  return (
    <TextField
      ref={(el: HTMLDivElement) => {
        // for some reason capturing the ref directly on TextField.TextArea works in Chrome
        // but not in webkit, so we capture the parent ref and query for the textarea
        textareaRef = el.querySelector("textarea")! as HTMLTextAreaElement;
      }}
      class={cx(
        styles.textField,
        local.size != "default" && styles[local.size],
        local.orientation == "horizontal" && styles[local.orientation],
        {
          [styles.inverted]: local.inverted,
          [styles.ghost]: local.ghost,
        },
      )}
      {...other}
    >
      <Orienter orientation={local.orientation} align={"start"}>
        <Label
          labelComponent={TextField.Label}
          descriptionComponent={TextField.Description}
          in={keepTruthy(
            props.orientation == "horizontal" && "Orienter-horizontal",
          )}
          {...withDefaults}
        />
        <TextField.TextArea
          class={cx({
            [styles.autoResize]: local.autoResize,
          })}
          onInput={(e) => {
            autoResize();

            if (!local.input.onInput) {
              return;
            }

            // Call original onInput if it exists
            if (typeof local.input.onInput === "function") {
              local.input.onInput(e);
            } else if (Array.isArray(local.input.onInput)) {
              local.input.onInput.forEach((handler) => handler(e));
            }
          }}
          {...local.input}
        />
      </Orienter>
    </TextField>
  );
};
