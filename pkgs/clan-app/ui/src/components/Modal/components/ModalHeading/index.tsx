import { Component, JSX, Show } from "solid-js";
import styles from "./ModalHeading.module.css";
import { Typography } from "@/src/components/Typography/Typography";

const ModalHeading: Component<{ text: string; tail?: JSX.Element }> = (
  props,
) => {
  return (
    <div class={styles.heading}>
      <div class={styles.headingInner}>
        <Typography
          hierarchy="label"
          family="mono"
          size="default"
          weight="medium"
        >
          {props.text}
        </Typography>
        <Show when={props.tail}>{props.tail}</Show>
      </div>
    </div>
  );
};
export default ModalHeading;
