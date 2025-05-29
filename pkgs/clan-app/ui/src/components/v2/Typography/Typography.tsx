import { type JSX } from "solid-js";
import { Dynamic } from "solid-js/web";
import cx from "classnames";
import "./Typography.css";

export type Tag = "span" | "p" | "h1" | "h2" | "h3" | "h4" | "div";
export type Hierarchy = "body" | "title" | "headline" | "label";
export type Weight = "normal" | "medium" | "bold";

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
}

export type AllowedSizes<H extends Hierarchy> = keyof SizeForHierarchy[H];

const sizeHierarchyMap: SizeForHierarchy = {
  body: {
    default: cx("font-size-default"),
    s: cx("font-size-s"),
    xs: cx("font-size-xs"),
    xxs: cx("font-size-xxs"),
  },
  headline: {
    default: cx("font-size-default"),
    m: cx("font-size-m"),
    l: cx("font-size-l"),
  },
  title: {
    default: cx("font-size-default"),
    // xs: cx("font-size-xs"),
    // s: cx("font-size-s"),
    m: cx("font-size-m"),
    l: cx("font-size-l"),
  },
  label: {
    default: cx("font-size-default"),
    s: cx("font-size-s"),
    xs: cx("font-size-xs"),
  },
};

const weightMap: Record<Weight, string> = {
  normal: cx("font-weight-normal"),
  medium: cx("font-weight-medium"),
  bold: cx("font-weight-bold"),
};

interface _TypographyProps<H extends Hierarchy> {
  hierarchy: H;
  size: AllowedSizes<H>;
  children: JSX.Element;
  weight?: Weight;
  inverted?: boolean;
  tag?: Tag;
  class?: string;
  classList?: Record<string, boolean>;
}

export const Typography = <H extends Hierarchy>(props: _TypographyProps<H>) => {
  return (
    <Dynamic
      component={props.tag || "span"}
      class={cx(
        "typography",
        weightMap[props.weight || "normal"],
        `font-${props.hierarchy}`,
        sizeHierarchyMap[props.hierarchy][props.size] as string,
        props.class,
      )}
      classList={props.classList}
    >
      {props.children}
    </Dynamic>
  );
};

export type TypographyProps = _TypographyProps<Hierarchy>;
