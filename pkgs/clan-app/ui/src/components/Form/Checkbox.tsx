import {
  CheckboxInputProps as KCheckboxInputProps,
  CheckboxRootProps as KCheckboxRootProps,
} from "@kobalte/core/checkbox";

import { Checkbox as KCheckbox } from "@kobalte/core";

import Icon from "@/src/components/Icon/Icon";

import cx from "classnames";
import { Label } from "./Label";
import { PolymorphicProps } from "@kobalte/core/polymorphic";
import "./Checkbox.css";
import { FieldProps } from "./Field";
import { Orienter } from "./Orienter";
import { Match, splitProps, Switch } from "solid-js";

export type CheckboxProps = FieldProps &
  KCheckboxRootProps & {
    input?: PolymorphicProps<"input", KCheckboxInputProps<"input">>;
  };

export const Checkbox = (props: CheckboxProps) => {
  // we need to separate output the input otherwise it interferes with prop binding
  const [_, rootProps] = splitProps(props, ["input"]);

  const [styleProps, otherRootProps] = splitProps(rootProps, [
    "class",
    "size",
    "orientation",
    "inverted",
    "ghost",
  ]);

  const alignment = () =>
    (props.orientation || "vertical") == "vertical" ? "start" : "center";

  const iconChecked = (
    <Icon
      icon="Checkmark"
      inverted={props.inverted}
      color="secondary"
      size="100%"
    />
  );

  const iconUnchecked = (
    <Icon
      icon="Close"
      inverted={props.inverted}
      color="secondary"
      size="100%"
    />
  );

  return (
    <KCheckbox.Root
      class={cx(
        styleProps.class,
        "form-field",
        "checkbox",
        styleProps.size,
        styleProps.orientation,
        {
          inverted: styleProps.inverted,
          ghost: styleProps.ghost,
        },
      )}
      {...otherRootProps}
    >
      {(state) => (
        <Orienter orientation={styleProps.orientation} align={alignment()}>
          <Label
            labelComponent={KCheckbox.Label}
            descriptionComponent={KCheckbox.Description}
            {...props}
          />
          <KCheckbox.Input {...props.input} />
          <KCheckbox.Control class="checkbox-control">
            <Switch>
              <Match when={!props.readOnly}>
                <KCheckbox.Indicator>{iconChecked}</KCheckbox.Indicator>
              </Match>
              <Match when={props.readOnly && state.checked()}>
                {iconChecked}
              </Match>
              <Match when={props.readOnly && !state.checked()}>
                {iconUnchecked}
              </Match>
            </Switch>
          </KCheckbox.Control>
        </Orienter>
      )}
    </KCheckbox.Root>
  );
};
