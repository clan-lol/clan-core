import { mergeProps, type ValidComponent, type JSX } from "solid-js";
import { Dynamic } from "solid-js/web";
import cx from "classnames";
import styles from "./Typography.module.css";
import { Color } from "@/src/components/colors";
import colorsStyles from "../colors.module.css";
import { getInClasses } from "@/src/util";

export type Hierarchy = "body" | "title" | "headline" | "label" | "teaser";
export type Weight = "normal" | "medium" | "bold";
export type Family = "regular" | "condensed" | "mono";
export type Transform = "uppercase" | "lowercase" | "capitalize";
export interface SizeForHierarchy {
  body: "default" | "s" | "xs" | "xxs";
  headline: "default" | "m" | "l" | "xl" | "xxl";
  title: "default" | "m" | "l";
  label: "default" | "s" | "xs" | "xxs";
  teaser: "default";
}
export interface TagForHierarchy {
  body: "span" | "p" | "div";
  headline: "h1" | "h2" | "h3" | "h4";
  title: "h1" | "h2" | "h3" | "h4";
  label: "span" | "div";
  teaser: "h1" | "h2" | "h3" | "h4";
}

const defaultFamilyMap = {
  body: "condensed",
  headline: "regular",
  title: "regular",
  label: "condensed",
  teaser: "regular",
} as const;

const defaultTagMap = {
  body: "p",
  headline: "h1",
  title: "h2",
  label: "span",
  teaser: "h3",
} as const;
export interface TypographyProps<H extends Hierarchy> {
  hierarchy: H;
  children: JSX.Element;
  size?: SizeForHierarchy[H];
  color?: Color;
  weight?: Weight;
  family?: Family;
  inverted?: boolean;
  tag?: TagForHierarchy[H];
  transform?: Transform;
  align?: "left" | "center" | "right";
  in?:
    | "Button"
    | "Label"
    | "Modal-title"
    | "TagSelect-label"
    | "Select-item-label"
    | "SelectService-item-description";
}

export const Typography = <H extends Hierarchy>(props: TypographyProps<H>) => {
  const local = mergeProps(
    {
      size: "default",
      color: "primary",
      weight: "normal",
      family: defaultFamilyMap[props.hierarchy],
      align: "left",
      tag: defaultTagMap[props.hierarchy],
    } as const,
    props,
  );

  return (
    <Dynamic
      component={local.tag as ValidComponent}
      class={cx(
        styles.typography,
        styles[local.hierarchy],
        styles[`family-${local.family}`],
        styles[`weight-${local.weight}`],
        local.size != "default" &&
          styles[
            `size-${local.size as Exclude<SizeForHierarchy[H], "default">}`
          ],
        styles[`align-${local.align}`],
        local.transform && styles[local.transform],
        colorsStyles[local.color],
        {
          [colorsStyles.inverted]: local.inverted,
        },
        getInClasses(styles, local.in),
      )}
    >
      {local.children}
    </Dynamic>
  );
};
