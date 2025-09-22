import styles from "./Fieldset.module.css";
import { JSX } from "solid-js";
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

export type FieldsetProps = Pick<FieldProps, "orientation" | "inverted"> & {
  legend?: string;
  error?: string;
  disabled?: boolean;
  name?: string;
  children: JSX.Element | ((props: FieldsetFieldProps) => JSX.Element);
};

export const Fieldset = (props: FieldsetProps) => {
  const children = () =>
    typeof props.children === "function"
      ? props.children(props)
      : props.children;

  return (
    <div
      role="group"
      class={cx(styles.fieldset, { [styles.inverted]: props.inverted })}
      aria-disabled={props.disabled || undefined}
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
      <div class={styles.fields}>{children()}</div>
      {props.error && (
        <div class={styles.error} role="alert">
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
    </div>
  );
};
