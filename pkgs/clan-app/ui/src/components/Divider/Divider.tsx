import styles from "./Divider.module.css";
import cx from "classnames";
import { Separator, SeparatorRootProps } from "@kobalte/core/separator";

export interface DividerProps extends Pick<SeparatorRootProps, "orientation"> {
  inverted?: boolean;
}

export const Divider = (props: DividerProps) => {
  const inverted = props.inverted || false;

  return (
    <Separator
      class={cx({ [styles.inverted]: inverted })}
      orientation={props.orientation}
    />
  );
};
