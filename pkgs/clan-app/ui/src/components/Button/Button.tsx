import { mergeProps, splitProps, type JSX } from "solid-js";
import cx from "classnames";
import { Typography } from "../Typography/Typography";
import { Button as KobalteButton } from "@kobalte/core/button";

import styles from "./Button.module.css";
import Icon, { IconVariant } from "@/src/components/Icon/Icon";
import { Loader } from "@/src/components/Loader/Loader";
import { getInClasses, joinByDash, keepTruthy } from "@/src/util";

type Size = "default" | "s" | "xs";
type Hierarchy = "primary" | "secondary";
type Elasticity = "default" | "fit";

export interface ButtonProps
  extends JSX.ButtonHTMLAttributes<HTMLButtonElement> {
  hierarchy?: Hierarchy;
  size?: Size;
  ghost?: boolean;
  children?: JSX.Element;
  icon?: IconVariant;
  endIcon?: IconVariant;
  loading?: boolean;
  elasticity?: Elasticity;
  in?:
    | "HostFileInput-horizontal"
    | "TagSelect"
    | "UpdateProgress"
    | "InstallProgress"
    | "FlashProgress"
    | "CheckHardware"
    | "ConfigureService";
}

export const Button = (props: ButtonProps) => {
  const [local, other] = splitProps(
    mergeProps(
      { size: "default", hierarchy: "primary", elasticity: "default" } as const,
      props,
    ),
    [
      "children",
      "hierarchy",
      "size",
      "ghost",
      "icon",
      "endIcon",
      "loading",
      "elasticity",
      "disabled",
      "in",
      "onClick",
    ],
  );

  return (
    <KobalteButton
      role="button"
      class={cx(
        styles.button, // default button class
        local.size != "default" && styles[local.size],
        styles[local.hierarchy],
        local.elasticity != "default" && local.elasticity,
        getInClasses(styles, local.in),
        {
          [styles.iconOnly]: local.icon && !local.children,
          [styles.hasIcon]: local.icon && local.children,
          [styles.hasEndIcon]: local.endIcon && local.children,
          [styles.loading]: local.loading,
          [styles.ghost]: local.ghost,
        },
      )}
      onClick={local.onClick}
      disabled={local.disabled ?? local.loading}
      {...other}
    >
      <Loader hierarchy={local.hierarchy} loading={local.loading} in="Button" />

      {local.icon && (
        <Icon
          icon={local.icon}
          in={keepTruthy(
            "Button",
            joinByDash("Button", local.hierarchy),
            local.size == "default" ? "" : joinByDash("Button", local.size),
          )}
        />
      )}

      {local.children && (
        <Typography
          hierarchy="label"
          size={local.size}
          inverted={local.hierarchy === "primary"}
          weight="bold"
          in="Button"
        >
          {local.children}
        </Typography>
      )}

      {local.endIcon && local.children && (
        <Icon
          icon={local.endIcon}
          in={keepTruthy(
            "Button",
            joinByDash("Button", local.hierarchy),
            local.size == "default" ? "" : joinByDash("Button", local.size),
          )}
        />
      )}
    </KobalteButton>
  );
};
