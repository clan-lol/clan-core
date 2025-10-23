import cx from "classnames";
import { JSX, mergeProps } from "solid-js";

import styles from "./Orienter.module.css";

interface OrienterProps {
  orientation?: "vertical" | "horizontal";
  align?: "center" | "start";
  children: JSX.Element;
}

export const Orienter = (props: OrienterProps) => {
  const local = mergeProps({ align: "center" } as const, props);

  return (
    <div
      class={cx(
        styles.orienter,
        styles[`align-${local.align}`],
        local.orientation && styles[local.orientation],
      )}
    >
      {local.children}
    </div>
  );
};
