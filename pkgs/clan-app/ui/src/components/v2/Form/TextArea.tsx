import {
  TextField,
  TextFieldRootProps,
  TextFieldTextAreaProps,
} from "@kobalte/core/text-field";

import cx from "classnames";
import { Label } from "./Label";
import { PolymorphicProps } from "@kobalte/core/polymorphic";

import "./TextInput.css";
import { FieldProps } from "./Field";

export type TextAreaProps = FieldProps &
  TextFieldRootProps & {
    input?: PolymorphicProps<"textarea", TextFieldTextAreaProps<"input">>;
  };

export const TextArea = (props: TextAreaProps) => (
  <TextField
    class={cx("form-field", "textarea", props.size, props.orientation, {
      inverted: props.inverted,
      ghost: props.ghost,
    })}
    {...props}
  >
    <Label
      labelComponent={TextField.Label}
      descriptionComponent={TextField.Description}
      {...props}
    />
    <TextField.TextArea {...props.input} />
  </TextField>
);
