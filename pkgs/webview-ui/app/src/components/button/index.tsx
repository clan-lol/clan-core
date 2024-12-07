import { splitProps, type JSX } from "solid-js";
import cx from "classnames";

type Variants = "dark" | "light";
type Size = "default" | "s";

const variantColors: Record<Variants, string> = {
  dark: cx(
    "border-secondary-950 bg-primary-900 text-white",
    "shadow-inner-primary",
    // Hover state
    // Focus state
    // Active state
    "hover:border-secondary-900 hover:bg-secondary-700",
    "focus:border-secondary-900",
    "active:border-secondary-900 active:shadow-inner-primary-active",
    // Disabled
    "disabled:bg-secondary-200 disabled:text-secondary-700 disabled:border-secondary-300",
  ),
  light: cx(
    "border-secondary-800 bg-secondary-100 text-secondary-800",
    "shadow-inner-secondary",
    // Hover state
    // Focus state
    // Active state
    "hover:bg-secondary-200 hover:text-secondary-900",
    "focus:bg-secondary-200 focus:text-secondary-900",
    "active:bg-secondary-200 active:text-secondary-950 active:shadow-inner-secondary-active",
    // Disabled
    "disabled:bg-secondary-50 disabled:text-secondary-200 disabled:border-secondary-700",
  ),
};

const sizePaddings: Record<Size, string> = {
  default: cx("rounded-[0.1875rem] px-4 py-2"),
  s: cx("rounded-sm py-[0.375rem] px-3"),
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
  return (
    <button
      class={cx(
        local.class,
        // Layout
        "inline-flex items-center flex-shrink gap-2 justify-center",
        // Styles
        "border border-solid",
        "p-4",
        sizePaddings[local.size || "default"],
        // Colors
        variantColors[local.variant || "dark"],
      )}
      {...other}
    >
      {local.startIcon && <span class="h-4">{local.startIcon}</span>}
      {local.children && <span>{local.children}</span>}
      {local.endIcon && <span class="h-4">{local.endIcon}</span>}
    </button>
  );
};
