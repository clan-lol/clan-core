import { Modal } from "../../components/Modal/Modal";
import cx from "classnames";
import styles from "./ListClansModal.module.css";
import { Typography } from "@/src/components/Typography/Typography";
import { Button } from "@/src/components/Button/Button";
import { navigateToOnboarding } from "@/src/hooks/clan";
import { useNavigate } from "@solidjs/router";
import { For, Show } from "solid-js";
import { activeClanURI, clanURIs, setActiveClanURI } from "@/src/stores/clan";
import { useClanListQuery } from "@/src/hooks/queries";
import { Alert } from "@/src/components/Alert/Alert";
import { NavSection } from "@/src/components/NavSection/NavSection";

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
      // this is the easiest way of reloading the clan
      window.location.reload();
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
        </div>
        <ul class={cx(styles.clans)}>
          <For each={clanList()}>
            {(clan) => (
              <li>
                <NavSection
                  label={clan.data.details.name}
                  description={clan.data.details.description ?? undefined}
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
