// Loader.tsx
import styles from "./Loader.module.css";
import cx from "classnames";

export type Hierarchy = "primary" | "secondary";

export interface LoaderProps {
  hierarchy?: Hierarchy;
}

export const Loader = (props: LoaderProps) => {
  return (
    <div class={cx(styles.loader, styles[props.hierarchy || "primary"])}>
      <div class={styles.wrapper}>
        <div class={styles.parent}></div>
      </div>
      <div class={styles.child}></div>
    </div>
  );
};
