import { type JSX } from "solid-js";
import { Dynamic } from "solid-js/web";
import cx from "classnames";
import "./Typography.css";
import { Color, fgClass } from "@/src/components/v2/colors";

export type Tag = "span" | "p" | "h1" | "h2" | "h3" | "h4" | "div";
export type Hierarchy = "body" | "title" | "headline" | "label" | "teaser";
export type Weight = "normal" | "medium" | "bold" | "light";
export type Family = "regular" | "condensed" | "mono";
export type Transform = "uppercase" | "lowercase" | "capitalize";

// type Size = "default" | "xs" | "s" | "m" | "l";
interface SizeForHierarchy {
  body: {
    default: string;
    s: string;
    xs: string;
    xxs: string;
  };
  label: {
    default: string;
    s: string;
    xs: string;
    xxs: string;
  };
  headline: {
    default: string;
    m: string;
    l: string;
  };
  title: {
    default: string;
    m: string;
    l: string;
  };
  teaser: {
    default: string;
  };
}

export type AllowedSizes<H extends Hierarchy> = keyof SizeForHierarchy[H];

const sizeHierarchyMap: SizeForHierarchy = {
  body: {
    default: cx("size-default"),
    s: cx("size-s"),
    xs: cx("size-xs"),
    xxs: cx("size-xxs"),
  },
  headline: {
    default: cx("size-default"),
    m: cx("size-m"),
    l: cx("size-l"),
  },
  title: {
    default: cx("size-default"),
    // xs: cx("size-xs"),
    // s: cx("size-s"),
    m: cx("size-m"),
    l: cx("size-l"),
  },
  label: {
    default: cx("size-default"),
    s: cx("size-s"),
    xs: cx("size-xs"),
    xxs: cx("size-xxs"),
  },
  teaser: {
    default: cx("size-default"),
  },
};

const defaultFamilyMap: Record<Hierarchy, Family> = {
  body: "condensed",
  label: "condensed",
  title: "regular",
  headline: "regular",
  teaser: "regular",
};

const weightMap: Record<Weight, string> = {
  normal: "weight-normal",
  medium: "weight-medium",
  bold: "weight-bold",
  light: "weight-light",
};

interface _TypographyProps<H extends Hierarchy> {
  hierarchy: H;
  size: AllowedSizes<H>;
  color?: Color;
  children: JSX.Element;
  weight?: Weight;
  family?: Family;
  inverted?: boolean;
  tag?: Tag;
  class?: string;
  transform?: Transform;
}

export const Typography = <H extends Hierarchy>(props: _TypographyProps<H>) => {
  const family = () =>
    `family-${props.family || defaultFamilyMap[props.hierarchy]}`;
  const hierarchy = () => props.hierarchy || "body";
  const size = () => sizeHierarchyMap[props.hierarchy][props.size] as string;
  const weight = () => weightMap[props.weight || "normal"];
  const color = () => fgClass(props.color, props.inverted);

  return (
    <Dynamic
      class={cx(
        "typography",
        hierarchy(),
        family(),
        weight(),
        size(),
        color(),
        props.transform,
        props.class,
      )}
      component={props.tag || "span"}
    >
      {props.children}
    </Dynamic>
  );
};

export type TypographyProps = _TypographyProps<Hierarchy>;
