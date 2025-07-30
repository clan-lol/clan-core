import { splitProps, type JSX, createSignal } from "solid-js";
import cx from "classnames";
import { Typography } from "../Typography/Typography";
import { Button as KobalteButton } from "@kobalte/core/button";

import "./Button.css";
import Icon, { IconVariant } from "@/src/components/Icon/Icon";
import { Loader } from "@/src/components/Loader/Loader";

export type Size = "default" | "s";
export type Hierarchy = "primary" | "secondary";

export type Action = () => Promise<void>;

export interface ButtonProps
  extends JSX.ButtonHTMLAttributes<HTMLButtonElement> {
  hierarchy?: Hierarchy;
  size?: Size;
  ghost?: boolean;
  children?: JSX.Element;
  icon?: IconVariant;
  startIcon?: IconVariant;
  endIcon?: IconVariant;
  class?: string;
  onAction?: Action;
}

const iconSizes: Record<Size, string> = {
  default: "1rem",
  s: "0.8125rem",
};

export const Button = (props: ButtonProps) => {
  const [local, other] = splitProps(props, [
    "children",
    "hierarchy",
    "size",
    "ghost",
    "icon",
    "startIcon",
    "endIcon",
    "class",
    "onAction",
  ]);

  const size = local.size || "default";
  const hierarchy = local.hierarchy || "primary";

  const [loading, setLoading] = createSignal(false);

  const onClick = async () => {
    if (!local.onAction) {
      console.error("this should not be possible");
      return;
    }

    setLoading(true);

    try {
      await local.onAction();
    } catch (error) {
      console.error("Error while executing action", error);
    }

    setLoading(false);
  };

  const iconSize = iconSizes[local.size || "default"];

  const loadingClass =
    "w-4 opacity-100 mr-[revert] transition-all duration-500 ease-linear";
  const idleClass =
    "w-0 opacity-0 top-0 left-0 -mr-2 transition-all duration-500 ease-linear";

  return (
    <KobalteButton
      class={cx(
        local.class,
        "button", // default button class
        size,
        hierarchy,
        {
          icon: local.icon,
          loading: loading(),
          ghost: local.ghost,
        },
      )}
      onClick={local.onAction ? onClick : undefined}
      {...other}
    >
      <Loader
        hierarchy={hierarchy}
        class={cx({ [idleClass]: !loading(), [loadingClass]: loading() })}
      />

      {local.startIcon && (
        <Icon icon={local.startIcon} class="icon-start" size={iconSize} />
      )}

      {local.icon && !local.children && (
        <Icon icon={local.icon} class="icon" size={iconSize} />
      )}

      {local.children && !local.icon && (
        <Typography
          class="label"
          hierarchy="label"
          family="mono"
          size={local.size || "default"}
          inverted={local.hierarchy === "primary"}
          weight="bold"
          tag="span"
        >
          {local.children}
        </Typography>
      )}

      {local.endIcon && (
        <Icon icon={local.endIcon} class="icon-end" size={iconSize} />
      )}
    </KobalteButton>
  );
};
