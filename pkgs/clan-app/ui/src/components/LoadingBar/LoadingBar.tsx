import { JSX } from "solid-js";
import styles from "./LoadingBar.module.css";
import cx from "classnames";

type LoadingBarProps = JSX.HTMLAttributes<HTMLDivElement> & {};
export const LoadingBar = (props: LoadingBarProps) => (
  <div {...props} class={cx(styles.loading_bar, props.class)} />
);
