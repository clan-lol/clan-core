import Clan from "@/logos/clan.svg";
import { Dynamic } from "solid-js/web";
import { Color, fgClass } from "@/src/components/colors";
import { JSX, splitProps } from "solid-js";
import cx from "classnames";

const logos = {
  Clan,
};

export type LogoVariant = keyof typeof logos;

export interface LogoProps extends JSX.SvgSVGAttributes<SVGElement> {
  class?: string;
  variant: LogoVariant;
  color?: Color;
  inverted?: boolean;
}

export const Logo = (props: LogoProps) => {
  const [local, iconProps] = splitProps(props, [
    "variant",
    "color",
    "class",
    "inverted",
  ]);

  const Logo = logos[local.variant];
  return (
    <Dynamic
      component={Logo}
      class={cx("icon", local.class, fgClass(local.color, local.inverted), {
        inverted: local.inverted,
      })}
      data-logo-name={local.variant}
    />
  );
};
