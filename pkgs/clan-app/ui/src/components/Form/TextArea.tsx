import {
  TextField,
  TextFieldRootProps,
  TextFieldTextAreaProps,
} from "@kobalte/core/text-field";

import cx from "classnames";
import { Label } from "./Label";
import { PolymorphicProps } from "@kobalte/core/polymorphic";
import { createEffect, createSignal, splitProps } from "solid-js";

import "./TextInput.css";
import { FieldProps } from "./Field";
import { Orienter } from "./Orienter";
import { keepTruthy } from "@/src/util";

export type TextAreaProps = FieldProps &
  TextFieldRootProps & {
    input: PolymorphicProps<"textarea", TextFieldTextAreaProps<"input">> & {
      autoResize?: boolean;
      minRows?: number;
      maxRows?: number;
    };
  };

export const TextArea = (props: TextAreaProps) => {
  let textareaRef: HTMLTextAreaElement;

  const [lineHeight, setLineHeight] = createSignal(0);

  const autoResize = () => {
    const input = props.input;

    if (!(textareaRef && input.autoResize && lineHeight() > 0)) return;

    // Reset height to auto to get accurate scrollHeight
    textareaRef.style.height = "auto";

    // Calculate min and max heights based on rows
    const minHeight = (input.minRows || 1) * lineHeight();
    const maxHeight = input.maxRows ? input.maxRows * lineHeight() : Infinity;

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
    if (textareaRef && props.input.autoResize) {
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
    if (props.input.autoResize && textareaRef) {
      // Access the value to create a dependency
      const _ = props.value || props.defaultValue || "";
      // Trigger resize on the next tick to ensure DOM is updated
      setTimeout(autoResize, 0);
    }
  });

  const input = props.input;

  // TextField.Textarea already has an `autoResize` prop
  // We filter our props out to avoid conflicting behaviour
  const [_, textareaProps] = splitProps(input, [
    "autoResize",
    "minRows",
    "maxRows",
  ]);

  const [styleProps, otherProps] = splitProps(props, [
    "class",
    "size",
    "orientation",
    "inverted",
    "ghost",
  ]);

  return (
    <TextField
      ref={(el: HTMLDivElement) => {
        // for some reason capturing the ref directly on TextField.TextArea works in Chrome
        // but not in webkit, so we capture the parent ref and query for the textarea
        textareaRef = el.querySelector("textarea")! as HTMLTextAreaElement;
      }}
      class={cx(
        styleProps.class,
        "form-field",
        "textarea",
        styleProps.size,
        styleProps.orientation,
        {
          inverted: styleProps.inverted,
          ghost: styleProps.ghost,
        },
      )}
      {...otherProps}
    >
      <Orienter orientation={styleProps.orientation} align={"start"}>
        <Label
          labelComponent={TextField.Label}
          descriptionComponent={TextField.Description}
          in={keepTruthy(
            props.orientation == "horizontal" && "Orienter-horizontal",
          )}
          {...props}
        />
        <TextField.TextArea
          class={cx(input.class, {
            "auto-resize": input.autoResize,
          })}
          onInput={(e) => {
            autoResize();

            if (!input.onInput) {
              return;
            }

            // Call original onInput if it exists
            if (typeof input.onInput === "function") {
              input.onInput(e);
            } else if (Array.isArray(input.onInput)) {
              input.onInput.forEach((handler) => handler(e));
            }
          }}
          {...textareaProps}
        />
      </Orienter>
    </TextField>
  );
};
