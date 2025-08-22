import { Modal } from "../../components/Modal/Modal";
import cx from "classnames";
import styles from "./ListClansModal.module.css";
import { Typography } from "@/src/components/Typography/Typography";
import { Button } from "@/src/components/Button/Button";
import { navigateToClan, navigateToOnboarding } from "@/src/hooks/clan";
import { useNavigate } from "@solidjs/router";
import { For, Show } from "solid-js";
import { activeClanURI, clanURIs, setActiveClanURI } from "@/src/stores/clan";
import { useClanListQuery } from "@/src/hooks/queries";
import { Alert } from "@/src/components/Alert/Alert";

export interface ListClansModalProps {
  onClose?: () => void;
  error?: {
    title: string;
    description: string;
  };
}

export const ListClansModal = (props: ListClansModalProps) => {
  const navigate = useNavigate();

  const query = useClanListQuery(clanURIs());

  // we only want clans we could interrogate successfully
  // todo how to surface the ones that failed to users?
  const clanList = () => query.filter((it) => it.isSuccess);

  const selectClan = (uri: string) => () => {
    if (uri == activeClanURI()) {
      navigateToClan(navigate, uri);
    } else {
      setActiveClanURI(uri);
    }
  };

  return (
    <Modal
      title="Select Clan"
      open
      onClose={props.onClose}
      class={cx(styles.modal)}
    >
      <div class={cx(styles.content)}>
        <Show when={props.error}>
          <Alert
            type="error"
            title={props.error?.title || ""}
            description={props.error?.description}
          />
        </Show>

        <div class={cx(styles.header)}>
          <Typography
            hierarchy="label"
            family="mono"
            size="xs"
            color="tertiary"
            transform="uppercase"
          >
            Your Clans
          </Typography>

          <Button
            hierarchy="secondary"
            ghost
            size="s"
            startIcon="Plus"
            onClick={() => {
              props.onClose?.();
              navigateToOnboarding(navigate, true);
            }}
          >
            Add Clan
          </Button>
        </div>
        <ul class={cx(styles.clans)}>
          <For each={clanList()}>
            {(clan) => (
              <li class={cx(styles.clan)}>
                <div class={cx(styles.meta)}>
                  <Typography hierarchy="label" weight="bold" size="default">
                    {clan.data.name}
                  </Typography>
                  <Typography hierarchy="body" size="s">
                    {clan.data.description}
                  </Typography>
                </div>

                <Button
                  hierarchy="secondary"
                  ghost
                  icon="CaretRight"
                  onClick={selectClan(clan.data.uri)}
                />
              </li>
            )}
          </For>
        </ul>
      </div>
    </Modal>
  );
};
