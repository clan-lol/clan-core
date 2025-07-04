import { Show } from "solid-js";
import { Typography } from "@/src/components/v2/Typography/Typography";
import { Tooltip as KTooltip } from "@kobalte/core/tooltip";
import Icon from "@/src/components/v2/Icon/Icon";
import { TextField } from "@kobalte/core/text-field";
import { Checkbox } from "@kobalte/core/checkbox";
import { Combobox } from "@kobalte/core/combobox";
import "./Label.css";
import cx from "classnames";

export type Size = "default" | "s";

export type LabelComponent =
  | typeof TextField.Label
  | typeof Checkbox.Label
  | typeof Combobox.Label;
export type DescriptionComponent =
  | typeof TextField.Description
  | typeof Checkbox.Description
  | typeof Combobox.Description;

export interface LabelProps {
  labelComponent: LabelComponent;
  descriptionComponent: DescriptionComponent;
  size?: Size;
  label?: string;
  description?: string;
  tooltip?: string;
  icon?: string;
  inverted?: boolean;
  validationState?: "valid" | "invalid";
}

export const Label = (props: LabelProps) => {
  const descriptionSize = () => (props.size == "default" ? "xs" : "xxs");

  return (
    <Show when={props.label}>
      <div class="form-label">
        <props.labelComponent>
          <Typography
            hierarchy="label"
            size={props.size || "default"}
            color={props.validationState == "invalid" ? "error" : "primary"}
            weight="bold"
            inverted={props.inverted}
          >
            {props.label}
          </Typography>
          {props.tooltip && (
            <KTooltip placement="top">
              <KTooltip.Trigger>
                <Icon
                  icon="Info"
                  color="tertiary"
                  inverted={props.inverted}
                  size={props.size == "default" ? "0.85em" : "0.75rem"}
                />
                <KTooltip.Portal>
                  <KTooltip.Content
                    class={cx("tooltip-content", { inverted: props.inverted })}
                  >
                    <Typography
                      hierarchy="body"
                      size="xs"
                      weight="medium"
                      inverted={!props.inverted}
                    >
                      {props.tooltip}
                    </Typography>
                    <KTooltip.Arrow />
                  </KTooltip.Content>
                </KTooltip.Portal>
              </KTooltip.Trigger>
            </KTooltip>
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
