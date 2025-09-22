export interface FieldProps {
  label?: string;
  labelWeight?: "bold" | "normal";
  description?: string;
  tooltip?: string;
  ghost?: boolean;

  size?: "default" | "s";
  orientation?: "horizontal" | "vertical";
  inverted?: boolean;
}
