import "./Alert.css";
import cx from "classnames";
import Icon, { IconVariant } from "@/src/components/Icon/Icon";
import { Typography } from "@/src/components/Typography/Typography";
import { Button } from "@kobalte/core/button";
import { Alert as KAlert } from "@kobalte/core/alert";
import { Show } from "solid-js";

export interface AlertProps {
  type: "success" | "error" | "warning" | "info";
  size?: "default" | "s";
  title: string;
  description?: string;
  icon?: IconVariant;
  onDismiss?: () => void;
}

export const Alert = (props: AlertProps) => {
  console.log("on dismiss", !!props.onDismiss);

  const size = () => props.size || "default";
  const titleSize = () => (size() == "default" ? "default" : "xs");
  const bodySize = () => (size() == "default" ? "xs" : "xxs");
  const iconSize = () => (size() == "default" ? "1rem" : "0.75rem");

  return (
    <KAlert
      class={cx("alert", props.type, {
        "has-icon": props.icon,
        "has-dismiss": props.onDismiss,
      })}
    >
      {props.icon && (
        <Icon icon={props.icon} color="inherit" size={iconSize()} />
      )}
      <div class="content">
        <Typography
          hierarchy="body"
          family="condensed"
          size={titleSize()}
          weight="bold"
          color="inherit"
        >
          {props.title}
        </Typography>
        <Show when={props.description}>
          <Typography
            hierarchy="body"
            family="condensed"
            size={bodySize()}
            color="inherit"
          >
            {props.description}
          </Typography>
        </Show>
      </div>
      {props.onDismiss && (
        <Button
          name="dismiss-alert"
          class="dismiss-trigger"
          onClick={props.onDismiss}
          aria-label={`Dismiss ${props.type} alert`}
        >
          <Icon icon="Close" color="primary" size="0.75rem" />
        </Button>
      )}
    </KAlert>
  );
};
