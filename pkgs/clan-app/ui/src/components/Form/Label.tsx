import { mergeProps, Show } from "solid-js";
import { Typography } from "@/src/components/Typography/Typography";
import { Tooltip } from "@/src/components/Tooltip/Tooltip";
import Icon from "@/src/components/Icon/Icon";
import { TextField } from "@kobalte/core/text-field";
import { Checkbox } from "@kobalte/core/checkbox";
import { Combobox } from "@kobalte/core/combobox";
import { Select } from "@kobalte/core/select";
import styles from "./Label.module.css";
import cx from "classnames";
import { getInClasses } from "@/src/util";

type Size = "default" | "s";

type LabelComponent =
  | typeof TextField.Label
  | typeof Checkbox.Label
  | typeof Combobox.Label
  | typeof Select.Label;

type DescriptionComponent =
  | typeof TextField.Description
  | typeof Checkbox.Description
  | typeof Combobox.Description
  | typeof Select.Description;

type In = "Orienter-horizontal";
export interface LabelProps {
  labelComponent: LabelComponent;
  descriptionComponent: DescriptionComponent;
  size?: Size;
  label?: string;
  labelWeight?: "bold" | "normal";
  description?: string;
  tooltip?: string;
  icon?: string;
  inverted?: boolean;
  readOnly?: boolean;
  validationState?: "valid" | "invalid";
  in?: In | In[];
}

export const Label = (props: LabelProps) => {
  const local = mergeProps(
    { size: "default", labelWeight: "bold", validationState: "valid" } as const,
    props,
  );
  const descriptionSize = () => (props.size == "default" ? "s" : "xs");

  return (
    <Show when={local.label}>
      <div class={cx(styles.label, getInClasses(styles, local.in))}>
        <local.labelComponent>
          <Typography
            hierarchy="label"
            size={local.size}
            color={local.validationState == "invalid" ? "error" : "primary"}
            weight={local.labelWeight}
            inverted={local.inverted}
            in="Label"
          >
            {local.label}
          </Typography>
          {local.tooltip && (
            <Tooltip
              placement="top"
              inverted={local.inverted}
              description={local.tooltip}
            >
              <Icon
                icon="Info"
                color="tertiary"
                inverted={local.inverted}
                size={local.size == "default" ? "0.85em" : "0.75rem"}
              />
            </Tooltip>
          )}
        </local.labelComponent>
        {local.description && (
          <local.descriptionComponent>
            <Typography
              hierarchy="body"
              size={descriptionSize()}
              color="secondary"
              weight="normal"
              inverted={local.inverted}
            >
              {local.description}
            </Typography>
          </local.descriptionComponent>
        )}
      </div>
    </Show>
  );
};
