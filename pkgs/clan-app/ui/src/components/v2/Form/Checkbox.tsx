import {
  Checkbox as KCheckbox,
  CheckboxInputProps as KCheckboxInputProps,
  CheckboxRootProps as KCheckboxRootProps,
} from "@kobalte/core/checkbox";
import Icon from "@/src/components/v2/Icon/Icon";

import cx from "classnames";
import { Label } from "./Label";
import { PolymorphicProps } from "@kobalte/core/polymorphic";
import "./Checkbox.css";
import { FieldProps } from "./Field";
import { Orienter } from "./Orienter";

export type CheckboxProps = FieldProps &
  KCheckboxRootProps & {
    input?: PolymorphicProps<"input", KCheckboxInputProps<"input">>;
  };

export const Checkbox = (props: CheckboxProps) => (
  <KCheckbox
    class={cx("form-field", "checkbox", props.size, props.orientation, {
      inverted: props.inverted,
      ghost: props.ghost,
    })}
    {...props}
  >
    <Orienter orientation={props.orientation} align={"start"}>
      <Label
        labelComponent={KCheckbox.Label}
        descriptionComponent={KCheckbox.Description}
        {...props}
      />
      <KCheckbox.Input {...props.input} />
      <KCheckbox.Control class="checkbox-control">
        <KCheckbox.Indicator>
          <Icon
            icon="Checkmark"
            inverted={props.inverted}
            color="secondary"
            size="100%"
          />
        </KCheckbox.Indicator>
      </KCheckbox.Control>
    </Orienter>
  </KCheckbox>
);
