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

export type TextInputProps = FieldProps &
  TextFieldRootProps & {
    icon?: IconVariant;
    input?: PolymorphicProps<"input", TextFieldInputProps<"input">>;
  };

export const TextInput = (props: TextInputProps) => {
  return (
    <TextField
      class={cx("form-field", "text", props.size, props.orientation, {
        inverted: props.inverted,
        ghost: props.ghost,
      })}
      {...props}
    >
      <Orienter orientation={props.orientation}>
        <Label
          labelComponent={TextField.Label}
          descriptionComponent={TextField.Description}
          {...props}
        />
        <div class="input-container">
          {props.icon && !props.readOnly && (
            <Icon
              icon={props.icon}
              inverted={props.inverted}
              color={props.disabled ? "tertiary" : "quaternary"}
            />
          )}
          <TextField.Input
            {...props.input}
            classList={{ "has-icon": props.icon && !props.readOnly }}
          />
        </div>
      </Orienter>
    </TextField>
  );
};
