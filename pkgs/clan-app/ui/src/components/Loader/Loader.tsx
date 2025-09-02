// Loader.tsx
import styles from "./Loader.module.css";
import cx from "classnames";

export type Hierarchy = "primary" | "secondary";

export interface LoaderProps {
  hierarchy?: Hierarchy;
  class?: string;
  size?: "default" | "l" | "xl";
}

export const Loader = (props: LoaderProps) => {
  const size = () => props.size || "default";

  return (
    <div
      class={cx(
        styles.loader,
        styles[props.hierarchy || "primary"],
        props.class,
        {
          [styles.sizeDefault]: size() === "default",
          [styles.sizeLarge]: size() === "l",
          [styles.sizeExtraLarge]: size() === "xl",
        },
      )}
    >
      <div class={styles.wrapper}>
        <div class={styles.parent}></div>
      </div>
      <div class={styles.child}></div>
    </div>
  );
};
