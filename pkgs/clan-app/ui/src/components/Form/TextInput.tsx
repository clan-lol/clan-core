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
import { splitProps } from "solid-js";

export type TextInputProps = FieldProps &
  TextFieldRootProps & {
    icon?: IconVariant;
    input?: PolymorphicProps<"input", TextFieldInputProps<"input">>;
  };

export const TextInput = (props: TextInputProps) => {
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
          {...props}
        />
        <div class="input-container">
          {props.icon && !props.readOnly && (
            <Icon
              icon={props.icon}
              inverted={styleProps.inverted}
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
