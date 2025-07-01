import "./Divider.css";
import cx from "classnames";
import { Orientation } from "@/src/components/v2/shared";

export interface DividerProps {
  inverted?: boolean;
  orientation?: Orientation;
}

export const Divider = (props: DividerProps) => {
  const inverted = props.inverted || false;
  const orientation = props.orientation || "horizontal";

  return <div class={cx("divider", orientation, { inverted: inverted })} />;
};
