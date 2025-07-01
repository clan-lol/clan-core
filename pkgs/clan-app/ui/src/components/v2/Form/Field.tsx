import { Size } from "@/src/components/v2/Form/Label";
import { Orientation } from "@/src/components/v2/shared";

export interface FieldProps {
  class?: string;
  label?: string;
  description?: string;
  tooltip?: string;
  ghost?: boolean;

  size?: Size;
  orientation?: Orientation;
  inverted?: boolean;
}
