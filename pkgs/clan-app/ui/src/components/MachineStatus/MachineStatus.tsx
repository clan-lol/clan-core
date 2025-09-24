import styles from "./MachineStatus.module.css";
import { Badge } from "@kobalte/core/badge";
import cx from "classnames";
import { Match, Show, Switch } from "solid-js";
import Icon from "../Icon/Icon";
import { Typography } from "@/src/components/Typography/Typography";
import { MachineStatus as MachineStatusModel } from "@/src/hooks/queries";
import { Loader } from "../Loader/Loader";

export interface MachineStatusProps {
  label?: boolean;
  status?: MachineStatusModel;
}

export const MachineStatus = (props: MachineStatusProps) => {
  // FIXME: this will break i18n in the future
  // remove the '_' from the enum
  // we will use css transform in the typography component to capitalize
  const statusText = () => props.status?.replaceAll("_", " ");

  // our implementation of machine status in the backend needs more time to bake, so for now we only display if a
  // machine is not installed

  return (
    <Switch>
      <Match when={!props.status}>
        <Loader />
      </Match>
      <Match when={props.status}>
        <Badge
          class={cx(styles.machineStatus, {
            [styles.online]: props.status == "online",
            [styles.offline]: props.status == "offline",
            [styles.outOfSync]: props.status == "out_of_sync",
          })}
          textValue={props.status}
        >
          {props.label && (
            <Typography
              hierarchy="label"
              size="xs"
              weight="medium"
              inverted={true}
              transform="capitalize"
            >
              {statusText()}
            </Typography>
          )}
          <Show
            when={props.status != "not_installed"}
            fallback={<Icon icon="Offline" inverted={true} />}
          >
            <div class={styles.indicator} />
          </Show>
        </Badge>
      </Match>
    </Switch>
  );
};
