import { createSignal, Setter } from "solid-js";
import { callApi, SuccessQuery } from "../../api";

import { A, useNavigate } from "@solidjs/router";
import { RndThumbnail } from "../noiseThumbnail";

import { Filter } from "../../routes/machines";
import { Typography } from "../Typography";
import "./css/index.css";
import { useClanContext } from "@/src/contexts/clan";

type MachineDetails = SuccessQuery<"list_machines">["data"][string];

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

  const { activeClanURI } = useClanContext();

  const navigate = useNavigate();

  const handleInstall = async () => {
    if (!info?.deploy?.targetHost || installing()) {
      return;
    }

    const active_clan = activeClanURI();
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
    const target_host = await callApi(
      "get_host",
      {
        field: "targetHost",
        flake: { identifier: active_clan },
        name: name,
      },
      {
        logging: { group_path: ["clans", active_clan, "machines", name] },
      },
    ).promise;

    if (target_host.status == "error") {
      console.error("No target host found for the machine");
      return;
    }

    if (target_host.data === null) {
      console.error("No target host found for the machine");
      return;
    }

    if (!target_host.data!.data) {
      console.error("No target host found for the machine");
      return;
    }

    setInstalling(true);
    await callApi("run_machine_install", {
      opts: {
        machine: {
          name: name,
          flake: {
            identifier: active_clan,
          },
        },
        no_reboot: true,
        debug: true,
        password: null,
      },
      target_host: target_host.data!.data,
    }).promise.finally(() => setInstalling(false));
  };

  const handleUpdate = async () => {
    if (!info?.deploy?.targetHost || installing()) {
      return;
    }

    const active_clan = activeClanURI();
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

    const target_host = await callApi(
      "get_host",
      {
        field: "targetHost",
        flake: { identifier: active_clan },
        name: name,
      },
      {
        logging: {
          group_path: ["clans", active_clan, "machines", name],
        },
      },
    ).promise;

    if (target_host.status == "error") {
      console.error("No target host found for the machine");
      return;
    }

    if (target_host.data === null) {
      console.error("No target host found for the machine");
      return;
    }

    if (!target_host.data!.data) {
      console.error("No target host found for the machine");
      return;
    }

    const build_host = await callApi(
      "get_host",
      {
        field: "buildHost",
        flake: { identifier: active_clan },
        name: name,
      },
      {
        logging: {
          group_path: ["clans", active_clan, "machines", name],
        },
      },
    ).promise;

    if (build_host.status == "error") {
      console.error("No target host found for the machine");
      return;
    }

    if (build_host.data === null) {
      console.error("No target host found for the machine");
      return;
    }

    await callApi(
      "run_machine_deploy",
      {
        machine: {
          name: name,
          flake: {
            identifier: active_clan,
          },
        },
        target_host: target_host.data!.data,
        build_host: build_host.data?.data || null,
      },
      {
        logging: {
          group_path: ["clans", active_clan, "machines", name],
        },
      },
    ).promise;

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
