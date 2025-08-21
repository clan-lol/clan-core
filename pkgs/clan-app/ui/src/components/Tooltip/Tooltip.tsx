import {
  Tooltip as KTooltip,
  TooltipRootProps as KTooltipRootProps,
} from "@kobalte/core/tooltip";
import cx from "classnames";
import { JSX } from "solid-js";
import styles from "./Tooltip.module.css";
import { Typography } from "../Typography/Typography";

export interface TooltipProps extends KTooltipRootProps {
  inverted?: boolean;
  children: JSX.Element;
  description: JSX.Element;
  animation?: "bounce";
}

export const Tooltip = (props: TooltipProps) => {
  return (
    <KTooltip {...props}>
      <KTooltip.Trigger>{props.children}</KTooltip.Trigger>
      <KTooltip.Portal>
        <KTooltip.Content
          class={cx(styles.tooltipContent, {
            [styles.inverted]: props.inverted,
            "animate-bounce": props.animation == "bounce",
          })}
        >
          {props.placement == "bottom" && <KTooltip.Arrow />}
          <Typography
            hierarchy="body"
            size="s"
            weight="medium"
            color="primary"
            inverted={!props.inverted}
          >
            {props.description}
          </Typography>
          {props.placement == "top" && <KTooltip.Arrow />}
        </KTooltip.Content>
      </KTooltip.Portal>
    </KTooltip>
  );
};
