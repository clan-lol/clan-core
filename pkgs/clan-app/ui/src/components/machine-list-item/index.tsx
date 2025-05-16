import { createSignal, For, Setter, Show } from "solid-js";
import { callApi, SuccessQuery } from "../../api";

import { activeURI } from "../../App";
import toast from "solid-toast";
import { A, useNavigate } from "@solidjs/router";
import { RndThumbnail } from "../noiseThumbnail";

import { Filter } from "../../routes/machines";
import { Typography } from "../Typography";
import "./css/index.css";

type MachineDetails = SuccessQuery<"list_inv_machines">["data"][string];

interface MachineListItemProps {
  name: string;
  info?: MachineDetails;
  nixOnly?: boolean;
  setFilter: Setter<Filter>;
}

export const MachineListItem = (props: MachineListItemProps) => {
  const { name, info, nixOnly } = props;

  // Bootstrapping
  const [installing, setInstalling] = createSignal<boolean>(false);

  // Later only updates
  const [updating, setUpdating] = createSignal<boolean>(false);

  const navigate = useNavigate();

  const handleInstall = async () => {
    if (!info?.deploy?.targetHost || installing()) {
      return;
    }

    const active_clan = activeURI();
    if (!active_clan) {
      console.error("No active clan selected");
      return;
    }
    if (!info?.deploy?.targetHost) {
      console.error(
        "Machine does not have a target host. Specify where the machine should be deployed.",
      );
      return;
    }
    setInstalling(true);
    await callApi("install_machine", {
      opts: {
        machine: {
          name: name,
          flake: {
            identifier: active_clan,
          },
          override_target_host: info?.deploy.targetHost,
        },
        no_reboot: true,
        debug: true,
        nix_options: [],
        password: null,
      },
    });
    setInstalling(false);
  };

  const handleUpdate = async () => {
    if (!info?.deploy?.targetHost || installing()) {
      return;
    }

    const active_clan = activeURI();
    if (!active_clan) {
      console.error("No active clan selected");
      return;
    }
    if (!info?.deploy.targetHost) {
      console.error(
        "Machine does not have a target host. Specify where the machine should be deployed.",
      );
      return;
    }
    setUpdating(true);
    await callApi("deploy_machine", {
      machine: {
        name: name,
        flake: {
          identifier: active_clan,
        },
        override_target_host: info?.deploy.targetHost,
      },
    });

    setUpdating(false);
  };
  return (
    <div class="machine-item">
      <A href={`/machines/${name}`}>
        <div class="machine-item__thumb-wrapper">
          <div class="machine-item__thumb">
            <RndThumbnail name={name} width={100} height={100} />
          </div>
          <div class="machine-item__pseudo" />
        </div>
        <header class="machine-item__header">
          <Typography
            class="text-center"
            hierarchy="body"
            size="s"
            weight="bold"
            color="primary"
          >
            {name}
          </Typography>
        </header>
      </A>
    </div>
  );
};
