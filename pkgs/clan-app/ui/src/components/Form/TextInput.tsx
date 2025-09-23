import {
  TextField,
  TextFieldInputProps,
  TextFieldRootProps,
} from "@kobalte/core/text-field";

import cx from "classnames";
import { Label } from "./Label";
import styles from "./TextField.module.css";
import { PolymorphicProps } from "@kobalte/core/polymorphic";
import { FieldProps } from "./Field";
import { Orienter } from "./Orienter";
import {
  Component,
  createEffect,
  createSignal,
  mergeProps,
  onMount,
  splitProps,
} from "solid-js";
import { keepTruthy } from "@/src/util";

export type TextInputProps = FieldProps &
  TextFieldRootProps & {
    input?: PolymorphicProps<"input", TextFieldInputProps<"input">>;
    startComponent?: Component<Pick<FieldProps, "inverted">>;
    endComponent?: Component<Pick<FieldProps, "inverted">>;
  };

export const TextInput = (props: TextInputProps) => {
  const withDefaults = mergeProps({ size: "default" } as const, props);
  const [local, other] = splitProps(withDefaults, [
    "size",
    "orientation",
    "inverted",
    "ghost",
    "input",
    "startComponent",
    "endComponent",
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
      <Orienter orientation={local.orientation}>
        <Label
          labelComponent={TextField.Label}
          descriptionComponent={TextField.Description}
          in={keepTruthy(
            props.orientation == "horizontal" && "Orienter-horizontal",
          )}
          {...withDefaults}
        />
        <div class={styles.inputContainer}>
          {local.startComponent && !other.readOnly && (
            <div ref={startComponentRef} class={styles.startComponent}>
              {local.startComponent({ inverted: local.inverted })}
            </div>
          )}
          <TextField.Input ref={inputRef} {...local.input} />
          {local.endComponent && !other.readOnly && (
            <div ref={endComponentRef} class={styles.endComponent}>
              {local.endComponent({ inverted: local.inverted })}
            </div>
          )}
        </div>
      </Orienter>
    </TextField>
  );
};
