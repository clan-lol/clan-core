import "./Fieldset.css";
import { Field, FieldProps, Orientation } from "./Field";
import { For } from "solid-js";
import cx from "classnames";
import { Typography } from "@/src/components/v2/Typography/Typography";

export interface FieldsetProps {
  legend: string;
  fields: FieldProps[];
  inverted?: boolean;
  disabled?: boolean;
  orientation?: Orientation;
  error?: string;
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
        <For each={props.fields}>
          {(fieldProps) => {
            return (
              <Field
                {...fieldProps}
                orientation={orientation()}
                disabled={props.disabled}
                inverted={props.inverted}
              />
            );
          }}
        </For>
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
