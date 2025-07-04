import "./Fieldset.css";
import { JSX } from "solid-js";
import cx from "classnames";
import { Typography } from "@/src/components/v2/Typography/Typography";
import { FieldProps } from "./Field";

export interface FieldsetProps extends FieldProps {
  legend: string;
  disabled: boolean;
  error?: string;
  fields: (props: FieldProps) => JSX.Element;
}

export const Fieldset = (props: FieldsetProps) => {
  const orientation = () => props.orientation || "vertical";

  return (
    <fieldset
      role="group"
      class={cx(orientation(), { inverted: props.inverted })}
      disabled={props.disabled}
    >
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
      <div class="fields">
        {props.fields({ ...props, orientation: orientation() })}
      </div>
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
