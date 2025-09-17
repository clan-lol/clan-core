// Loader.tsx
import { mergeProps } from "solid-js";
import styles from "./Loader.module.css";
import cx from "classnames";

export type Hierarchy = "primary" | "secondary";

export interface LoaderProps {
  hierarchy?: Hierarchy;
  size?: "default" | "l" | "xl";
  loading?: boolean;
  in?: "Button";
}

export const Loader = (props: LoaderProps) => {
  const local = mergeProps(
    { hierarchy: "primary", size: "default", loading: false } as const,
    props,
  );

  return (
    <div
      class={cx(
        styles.loader,
        styles[local.hierarchy],
        local.in ? styles[`in-${local.in}` as `in-${typeof local.in}`] : "",
        {
          [styles.sizeDefault]: local.size === "default",
          [styles.sizeLarge]: local.size === "l",
          [styles.sizeExtraLarge]: local.size === "xl",
          [styles.loading]: local.loading,
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
