import { splitProps, type JSX } from "solid-js";
import cx from "classnames";
import { Typography } from "../Typography";
//import './css/index.css'
import "./css/index.css";

type Variants = "dark" | "light" | "ghost";
type Size = "default" | "s";

const variantColors: (
  disabled: boolean | undefined,
) => Record<Variants, string> = (disabled) => ({
  dark: cx(
    "button--dark",
    !disabled && "button--dark-hover", // Hover state
    !disabled && "button--dark-focus", // Focus state
    !disabled && "button--dark-active", // Active state
    // Disabled
    "disabled:bg-secondary-200 disabled:text-secondary-700 disabled:border-secondary-300",
  ),
  light: cx(
    "button--light",

    !disabled && "button--light-hover", // Hover state
    !disabled && "button--light-focus", // Focus state
    !disabled && "button--light-active", // Active state
  ),
  ghost: cx(
    // "shadow-inner-secondary",
    !disabled && "hover:bg-secondary-200 hover:text-secondary-900", // Hover state
    !disabled && "focus:bg-secondary-200 focus:text-secondary-900", // Focus state
    !disabled && "button--light-active", // Active state
  ),
});

const sizePaddings: Record<Size, string> = {
  default: cx("button--default"),
  s: cx("button button--small"), //cx("rounded-sm py-[0.375rem] px-3"),
};

const sizeFont: Record<Size, string> = {
  default: cx("text-[0.8125rem]"),
  s: cx("text-[0.75rem]"),
};

interface ButtonProps extends JSX.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variants;
  size?: Size;
  children?: JSX.Element;
  startIcon?: JSX.Element;
  endIcon?: JSX.Element;
  class?: string;
}
export const Button = (props: ButtonProps) => {
  const [local, other] = splitProps(props, [
    "children",
    "variant",
    "size",
    "startIcon",
    "endIcon",
    "class",
  ]);

  const buttonInvertion = (variant: Variants) => {
    return !(!variant || variant === "ghost" || variant === "light");
  };

  return (
    <button
      class={cx(
        local.class,
        "button", // default button class
        variantColors(props.disabled)[local.variant || "dark"], // button appereance
        sizePaddings[local.size || "default"], // button size
      )}
      {...other}
    >
      {local.startIcon && (
        <span class="button__icon--start">{local.startIcon}</span>
      )}
      {local.children && (
        <Typography
          class="button__label"
          hierarchy="label"
          size={local.size || "default"}
          color="inherit"
          inverted={buttonInvertion(local.variant || "dark")}
          weight="medium"
          tag="span"
        >
          {local.children}
        </Typography>
      )}
      {local.endIcon && <span class="button__icon--end">{local.endIcon}</span>}
    </button>
  );
};
