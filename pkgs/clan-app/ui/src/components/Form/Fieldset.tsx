import "./Fieldset.css";
import { JSX, splitProps } from "solid-js";
import cx from "classnames";
import { Typography } from "@/src/components/Typography/Typography";
import { FieldProps } from "./Field";

export type FieldsetFieldProps = Pick<
  FieldProps,
  "orientation" | "inverted"
> & {
  error?: string;
  disabled?: boolean;
};

export interface FieldsetProps
  extends Pick<FieldProps, "orientation" | "inverted"> {
  legend?: string;
  disabled?: boolean;
  error?: string;
  children: (props: FieldsetFieldProps) => JSX.Element;
}

export const Fieldset = (props: FieldsetProps) => {
  const orientation = () => props.orientation || "vertical";

  const [fieldProps] = splitProps(props, [
    "orientation",
    "inverted",
    "disabled",
    "error",
  ]);

  return (
    <fieldset
      role="group"
      class={cx({ inverted: props.inverted })}
      disabled={props.disabled || false}
    >
      {props.legend && (
        <legend>
          <Typography
            hierarchy="label"
            family="mono"
            size="default"
            weight="normal"
            color="tertiary"
            transform="uppercase"
            inverted={props.inverted}
          >
            {props.legend}
          </Typography>
        </legend>
      )}
      <div class="fields">{props.children(fieldProps)}</div>
      {props.error && (
        <div class="error" role="alert">
          <Typography
            hierarchy="body"
            size="xxs"
            weight="medium"
            color="error"
            inverted={props.inverted}
          >
            {props.error}
          </Typography>
        </div>
      )}
    </fieldset>
  );
};
