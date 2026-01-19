import cx from "classnames";
import { Component, ComponentProps, mergeProps, splitProps } from "solid-js";

import { Dynamic } from "solid-js/web";
import styles from "./Icon.module.css";
import { Color } from "../colors";
import colorsStyles from "../colors.module.css";
import { getInClasses, mapObjectKeys } from "@/src/util";

const icons = mapObjectKeys(
  import.meta.glob<Component<ComponentProps<"svg">>>(
    "../../assets/icons/*.svg",
    {
      eager: true,
      import: "default",
    },
  ),
  ([name]) => {
    const result = /^\.\.\/\.\.\/assets\/icons\/(.+?)\.svg$/.exec(name);
    if (!result) {
      throw new Error("Failed to extract the icon name from import.meta.glob");
    }
    return result[1];
  },
);

type In =
  | "Button"
  | "Button-primary"
  | "Button-secondary"
  | "Button-s"
  | "Button-xs"
  | "MachineTags"
  | "MachineTags-s"
  | "ConfigureRole"
  // TODO: better name
  | "WorkflowPanelTitle"
  | "SidebarBody-AccordionTrigger";

const Icon: Component<
  ComponentProps<"svg"> & {
    name: string;
    size?: number | string;
    color?: Color;
    inverted?: boolean;
    in?: In | In[];
  }
> = (props) => {
  const [local, iconProps] = splitProps(
    mergeProps({ color: "primary", size: "1em" } as const, props),
    ["name", "color", "size", "inverted", "in"],
  );
  return (
    <Dynamic
      component={icons[local.name]}
      class={cx(
        styles.icon,
        getInClasses(styles, local.in),
        local.color && colorsStyles[local.color],
        {
          [colorsStyles.inverted]: local.inverted,
        },
      )}
      {...iconProps}
      width={local.size}
      height={local.size}
      ref={iconProps.ref}
    />
  );
};

export default Icon;
