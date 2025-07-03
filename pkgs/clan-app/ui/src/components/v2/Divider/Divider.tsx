import "./Divider.css";
import cx from "classnames";

export interface DividerProps {
  inverted?: boolean;
  orientation?: "horizontal" | "vertical";
}

export const Divider = (props: DividerProps) => {
  const inverted = props.inverted || false;
  const orientation = () => props.orientation || "horizontal";

  return <div class={cx("divider", orientation(), { inverted: inverted })} />;
};
