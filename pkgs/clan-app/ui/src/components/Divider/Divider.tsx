import "./Divider.css";
import cx from "classnames";
import { Separator, SeparatorRootProps } from "@kobalte/core/separator";

export interface DividerProps extends Pick<SeparatorRootProps, "orientation"> {
  inverted?: boolean;
  class?: string;
}

export const Divider = (props: DividerProps) => {
  const inverted = props.inverted || false;

  return (
    <Separator
      class={cx({ inverted: inverted }, props?.class)}
      orientation={props.orientation}
    />
  );
};
