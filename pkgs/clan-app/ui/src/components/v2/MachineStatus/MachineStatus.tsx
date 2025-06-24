import "./MachineStatus.css";

import { Badge } from "@kobalte/core/badge";
import cx from "classnames";
import { Show } from "solid-js";
import Icon from "../Icon/Icon";
import { Typography } from "@/src/components/v2/Typography/Typography";

export type MachineStatus =
  | "Online"
  | "Offline"
  | "Installed"
  | "Not Installed";

export interface MachineStatusProps {
  label?: boolean;
  status: MachineStatus;
}

export const MachineStatus = (props: MachineStatusProps) => (
  <Badge
    class={cx("machine-status", {
      online: props.status == "Online",
      offline: props.status == "Offline",
      installed: props.status == "Installed",
      "not-installed": props.status == "Not Installed",
    })}
    textValue={props.status}
  >
    {props.label && (
      <Typography hierarchy="label" size="xs" weight="medium" inverted={true}>
        {props.status}
      </Typography>
    )}
    <Show
      when={props.status == "Not Installed"}
      fallback={<div class="indicator" />}
    >
      <Icon icon="Offline" inverted={true} />
    </Show>
  </Badge>
);
