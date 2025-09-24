import Clan from "@/logos/clan.svg";
import { Dynamic } from "solid-js/web";
import { Color } from "@/src/components/colors";
import colorsStyles from "../colors.module.css";
import { JSX, mergeProps } from "solid-js";
import cx from "classnames";

const logos = {
  Clan,
};

export type LogoVariant = keyof typeof logos;

export interface LogoProps extends JSX.SvgSVGAttributes<SVGElement> {
  variant: LogoVariant;
  color?: Color;
  inverted?: boolean;
}

export const Logo = (props: LogoProps) => {
  const local = mergeProps({ color: "primary" } as const, props);
  const Logo = logos[local.variant];
  return (
    <Dynamic
      component={Logo}
      class={cx(local.color && colorsStyles[local.color], {
        [colorsStyles.inverted]: local.inverted,
      })}
      data-logo-name={local.variant}
    />
  );
};
