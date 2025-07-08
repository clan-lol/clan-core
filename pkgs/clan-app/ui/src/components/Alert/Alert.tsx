import "./Alert.css";
import cx from "classnames";
import Icon, { IconVariant } from "@/src/components/Icon/Icon";
import { Typography } from "@/src/components/Typography/Typography";
import { Button } from "@kobalte/core/button";
import { Alert as KAlert } from "@kobalte/core/alert";

export interface AlertProps {
  type: "success" | "error" | "warning" | "info";
  title: string;
  description: string;
  icon?: IconVariant;
  onDismiss?: () => void;
}

export const Alert = (props: AlertProps) => (
  <KAlert
    class={cx("alert", props.type, {
      "has-icon": props.icon,
      "has-dismiss": props.onDismiss,
    })}
  >
    {props.icon && <Icon icon={props.icon} color="inherit" size="1rem" />}
    <div class="content">
      <Typography hierarchy="body" size="default" weight="bold" color="inherit">
        {props.title}
      </Typography>
      <Typography hierarchy="body" size="xs" color="inherit">
        {props.description}
      </Typography>
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
