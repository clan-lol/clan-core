import cx from "classnames";
import { JSX } from "solid-js";

import "./Orienter.css";

export interface OrienterProps {
  orientation?: "vertical" | "horizontal";
  align?: "center" | "start";
  children: JSX.Element;
}

export const Orienter = (props: OrienterProps) => {
  const alignment = () => `align-${props.align || "center"}`;

  return (
    <div class={cx("orienter", alignment(), props.orientation)}>
      {props.children}
    </div>
  );
};
