export type Color =
  | "primary"
  | "secondary"
  | "tertiary"
  | "quaternary"
  | "error"
  | "inherit";

export const AllColors: Color[] = [
  "primary",
  "secondary",
  "tertiary",
  "quaternary",
  "error",
  "inherit",
];

const colorMap: Record<Color, string> = {
  primary: "fg-def-1",
  secondary: "fg-def-2",
  tertiary: "fg-def-3",
  quaternary: "fg-def-4",
  error: "fg-semantic-error-4",
  inherit: "text-inherit",
};

const invertedColorMap: Record<Color, string> = {
  primary: "fg-inv-1",
  secondary: "fg-inv-2",
  tertiary: "fg-inv-3",
  quaternary: "fg-inv-4",
  error: "fg-semantic-error-2",
  inherit: "text-inherit",
};

export const fgClass = (
  color: Color | "inherit" = "primary",
  inverted = false,
) => {
  if (color === "inherit") {
    return "text-inherit";
  }

  return inverted ? invertedColorMap[color] : colorMap[color];
};
