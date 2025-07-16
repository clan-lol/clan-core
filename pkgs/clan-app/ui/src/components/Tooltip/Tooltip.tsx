import "./Tooltip.css";
import {
  Tooltip as KTooltip,
  TooltipRootProps as KTooltipRootProps,
} from "@kobalte/core/tooltip";
import cx from "classnames";
import { JSX } from "solid-js";

export interface TooltipProps extends KTooltipRootProps {
  inverted?: boolean;
  trigger: JSX.Element;
  children: JSX.Element;
  animation?: "bounce";
}

export const Tooltip = (props: TooltipProps) => {
  return (
    <KTooltip {...props}>
      <KTooltip.Trigger>{props.trigger}</KTooltip.Trigger>
      <KTooltip.Portal>
        <KTooltip.Content
          class={cx("tooltip-content", {
            inverted: props.inverted,
            "animate-bounce": props.animation == "bounce",
          })}
        >
          {props.placement == "bottom" && <KTooltip.Arrow />}
          {props.children}
          {props.placement == "top" && <KTooltip.Arrow />}
        </KTooltip.Content>
      </KTooltip.Portal>
    </KTooltip>
  );
};
