import {
  CheckboxInputProps as KCheckboxInputProps,
  CheckboxRootProps as KCheckboxRootProps,
  Checkbox as KCheckbox,
} from "@kobalte/core/checkbox";

import Icon from "@/src/components/Icon/Icon";

import cx from "classnames";
import { Label } from "./Label";
import { PolymorphicProps } from "@kobalte/core/polymorphic";
import styles from "./Checkbox.module.css";
import { FieldProps } from "./Field";
import { Orienter } from "./Orienter";
import { Match, mergeProps, splitProps, Switch } from "solid-js";
import { keepTruthy } from "@/src/util";

export type CheckboxProps = FieldProps &
  KCheckboxRootProps & {
    input?: PolymorphicProps<"input", KCheckboxInputProps<"input">>;
  };

export const Checkbox = (props: CheckboxProps) => {
  const withDefaults = mergeProps(
    { size: "default", orientation: "vertical" } as const,
    props,
  );
  const [local, other] = splitProps(withDefaults, [
    "size",
    "orientation",
    "inverted",
    "ghost",
    "input",
  ]);

  const iconChecked = (
    <Icon
      icon="Checkmark"
      inverted={local.inverted}
      color="secondary"
      size="100%"
    />
  );

  const iconUnchecked = (
    <Icon
      icon="Close"
      inverted={local.inverted}
      color="secondary"
      size="100%"
    />
  );

  return (
    <KCheckbox
      class={cx(
        styles.checkbox,
        local.size != "default" && styles[local.size],
        {
          [styles.inverted]: local.inverted,
        },
      )}
      {...other}
    >
      {(state) => (
        <Orienter
          orientation={local.orientation}
          align={local.orientation == "vertical" ? "start" : "center"}
        >
          <Label
            labelComponent={KCheckbox.Label}
            descriptionComponent={KCheckbox.Description}
            in={keepTruthy(
              local.orientation == "horizontal" && "Orienter-horizontal",
            )}
            {...withDefaults}
          />
          <KCheckbox.Input {...local.input} />
          <KCheckbox.Control class={styles.checkboxControl}>
            <Switch>
              <Match when={!other.readOnly}>
                <KCheckbox.Indicator>{iconChecked}</KCheckbox.Indicator>
              </Match>
              <Match when={state.checked()}>{iconChecked}</Match>
              <Match when={true}>{iconUnchecked}</Match>
            </Switch>
          </KCheckbox.Control>
        </Orienter>
      )}
    </KCheckbox>
  );
};
