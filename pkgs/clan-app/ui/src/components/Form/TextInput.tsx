import {
  TextField,
  TextFieldInputProps,
  TextFieldRootProps,
} from "@kobalte/core/text-field";
import Icon, { IconVariant } from "@/src/components/Icon/Icon";

import cx from "classnames";
import { Label } from "./Label";
import "./TextInput.css";
import { PolymorphicProps } from "@kobalte/core/polymorphic";
import { FieldProps } from "./Field";
import { Orienter } from "./Orienter";
import {
  Component,
  createEffect,
  createSignal,
  onMount,
  splitProps,
} from "solid-js";
import { keepTruthy } from "@/src/util";

export type TextInputProps = FieldProps &
  TextFieldRootProps & {
    icon?: IconVariant;
    input?: PolymorphicProps<"input", TextFieldInputProps<"input">>;
    startComponent?: Component<Pick<FieldProps, "inverted">>;
    endComponent?: Component<Pick<FieldProps, "inverted">>;
  };

export const TextInput = (props: TextInputProps) => {
  const [styleProps, otherProps] = splitProps(props, [
    "class",
    "size",
    "orientation",
    "inverted",
    "ghost",
  ]);

  let inputRef: HTMLInputElement | undefined;
  let startComponentRef: HTMLDivElement | undefined;
  let endComponentRef: HTMLDivElement | undefined;

  const [startComponentSize, setStartComponentSize] = createSignal({
    width: 0,
    height: 0,
  });
  const [endComponentSize, setEndComponentSize] = createSignal({
    width: 0,
    height: 0,
  });

  onMount(() => {
    if (startComponentRef) {
      const rect = startComponentRef.getBoundingClientRect();
      setStartComponentSize({ width: rect.width, height: rect.height });
    }
    if (endComponentRef) {
      const rect = endComponentRef.getBoundingClientRect();
      setEndComponentSize({ width: rect.width, height: rect.height });
    }
  });

  createEffect(() => {
    if (inputRef) {
      const padding = props.size == "s" ? 6 : 8;

      inputRef.style.paddingLeft = `${startComponentSize().width + padding * 2}px`;
      inputRef.style.paddingRight = `${endComponentSize().width + padding * 2}px`;
    }
  });

  return (
    <TextField
      class={cx(
        styleProps.class,
        "form-field",
        "text",
        styleProps.size,
        styleProps.orientation,
        {
          inverted: styleProps.inverted,
          ghost: styleProps.ghost,
        },
      )}
      {...otherProps}
    >
      <Orienter orientation={styleProps.orientation}>
        <Label
          labelComponent={TextField.Label}
          descriptionComponent={TextField.Description}
          in={keepTruthy(
            props.orientation == "horizontal" && "Orienter-horizontal",
          )}
          {...props}
        />
        <div class="input-container">
          {props.startComponent && !props.readOnly && (
            <div ref={startComponentRef} class="start-component">
              {props.startComponent({ inverted: props.inverted })}
            </div>
          )}
          {props.icon && !props.readOnly && (
            <Icon
              icon={props.icon}
              inverted={styleProps.inverted}
              color={props.disabled ? "tertiary" : "quaternary"}
            />
          )}
          <TextField.Input
            ref={inputRef}
            {...props.input}
            class={cx({
              "has-icon": props.icon && !props.readOnly,
            })}
          />
          {props.endComponent && !props.readOnly && (
            <div ref={endComponentRef} class="end-component">
              {props.endComponent({ inverted: props.inverted })}
            </div>
          )}
        </div>
      </Orienter>
    </TextField>
  );
};
