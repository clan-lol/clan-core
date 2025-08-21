import { Show } from "solid-js";
import { Typography } from "@/src/components/Typography/Typography";
import { Tooltip } from "@/src/components/Tooltip/Tooltip";
import Icon from "@/src/components/Icon/Icon";
import { TextField } from "@kobalte/core/text-field";
import { Checkbox } from "@kobalte/core/checkbox";
import { Combobox } from "@kobalte/core/combobox";
import { Select } from "@kobalte/core/select";
import "./Label.css";

export type Size = "default" | "s";

export type LabelComponent =
  | typeof TextField.Label
  | typeof Checkbox.Label
  | typeof Combobox.Label
  | typeof Select.Label;

export type DescriptionComponent =
  | typeof TextField.Description
  | typeof Checkbox.Description
  | typeof Combobox.Description
  | typeof Select.Description;

export interface LabelProps {
  labelComponent: LabelComponent;
  descriptionComponent: DescriptionComponent;
  size?: Size;
  label?: string;
  description?: string;
  tooltip?: string;
  icon?: string;
  inverted?: boolean;
  readOnly?: boolean;
  validationState?: "valid" | "invalid";
}

export const Label = (props: LabelProps) => {
  const descriptionSize = () => (props.size == "default" ? "s" : "xs");

  return (
    <Show when={props.label}>
      <div class="form-label">
        <props.labelComponent>
          <Typography
            hierarchy="label"
            size={props.size || "default"}
            color={props.validationState == "invalid" ? "error" : "primary"}
            weight={props.readOnly ? "normal" : "bold"}
            inverted={props.inverted}
          >
            {props.label}
          </Typography>
          {props.tooltip && (
            <Tooltip
              placement="top"
              inverted={props.inverted}
              description={props.tooltip}
            >
              <Icon
                icon="Info"
                color="tertiary"
                inverted={props.inverted}
                size={props.size == "default" ? "0.85em" : "0.75rem"}
              />
            </Tooltip>
          )}
        </props.labelComponent>
        {props.description && (
          <props.descriptionComponent>
            <Typography
              hierarchy="body"
              size={descriptionSize()}
              color="secondary"
              weight="normal"
              inverted={props.inverted}
            >
              {props.description}
            </Typography>
          </props.descriptionComponent>
        )}
      </div>
    </Show>
  );
};
