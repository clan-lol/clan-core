export interface FieldProps {
  class?: string;
  label?: string;
  description?: string;
  tooltip?: string;
  ghost?: boolean;

  size?: "default" | "s";
  orientation?: "horizontal" | "vertical";
  inverted?: boolean;
}
