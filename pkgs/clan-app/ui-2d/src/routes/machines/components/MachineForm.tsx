import { callApi, OperationResponse } from "@/src/api";
import { createForm, ResponseData } from "@modular-forms/solid";
import { useNavigate } from "@solidjs/router";
import { useQuery, useQueryClient } from "@tanstack/solid-query";
import { createSignal } from "solid-js";
import { Button } from "@/src/components/Button/Button";
import { useClanContext } from "@/src/contexts/clan";
import { MachineAvatar } from "./MachineAvatar";
import toast from "solid-toast";
import { MachineActionsBar } from "./MachineActionsBar";
import { MachineGeneralFields } from "./MachineGeneralFields";
import { MachineHardwareInfo } from "./MachineHardwareInfo";

type DetailedMachineType = Extract<
  OperationResponse<"get_machine_details">,
  { status: "success" }
>["data"];

interface MachineFormProps {
  detailed: DetailedMachineType;
}

export function MachineForm(props: MachineFormProps) {
  const { detailed } = props;

  const [formStore, { Form, Field }] = createForm<
    DetailedMachineType,
    ResponseData
  >({
    initialValues: detailed,
  });

  const [isUpdating, setIsUpdating] = createSignal(false);

  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { activeClanURI } = useClanContext();

  const handleSubmit = async (values: DetailedMachineType) => {
    console.log("submitting", values);

    const curr_uri = activeClanURI();
    if (!curr_uri) {
      return;
    }

    await callApi("set_machine", {
      machine: {
        name: detailed.machine.name || "My machine",
        flake: {
          identifier: curr_uri,
        },
      },
      update: {
        ...values.machine,
        tags: Array.from(values.machine.tags || detailed.machine.tags || []),
      },
    }).promise;

    await queryClient.invalidateQueries({
      queryKey: [
        curr_uri,
        "machine",
        detailed.machine.name,
        "get_machine_details",
      ],
    });

    return null;
  };

  const generatorsQuery = useQuery(() => ({
    queryKey: [activeClanURI(), detailed.machine.name, "generators"],
    queryFn: async () => {
      const machine_name = detailed.machine.name;
      const base_dir = activeClanURI();
      if (!machine_name || !base_dir) {
        return [];
      }
      const result = await callApi(
        "get_generators_closure",
        {
          base_dir: base_dir,
          machine_name: machine_name,
        },
        {
          logging: {
            group: { name: machine_name, flake: { identifier: base_dir } },
          },
        },
      ).promise;
      if (result.status === "error") throw new Error("Failed to fetch data");
      return result.data;
    },
  }));

  const handleUpdateButton = async () => {
    await generatorsQuery.refetch();

    if (
      generatorsQuery.data?.some((generator) => generator.prompts?.length !== 0)
    ) {
      navigate(`/machines/${detailed.machine.name || ""}/vars?action=update`);
    } else {
      handleUpdate();
    }
  };

  const handleUpdate = async () => {
    if (isUpdating()) {
      return;
    }
    const curr_uri = activeClanURI();
    if (!curr_uri) {
      return;
    }
    const machine = detailed.machine.name;
    if (!machine) {
      toast.error("Machine is required");
      return;
    }

    const target = await callApi(
      "get_host",
      {
        field: "targetHost",
        name: machine,
        flake: {
          identifier: curr_uri,
        },
      },
      {
        logging: { group: { name: machine, flake: { identifier: curr_uri } } },
      },
    ).promise;

    if (target.status === "error") {
      toast.error("Failed to get target host");
      return;
    }

    if (!target.data) {
      toast.error("Target host is required");
      return;
    }
    const target_host = target.data.data;

    setIsUpdating(true);
    const r = await callApi(
      "deploy_machine",
      {
        machine: {
          name: machine,
          flake: {
            identifier: curr_uri,
          },
        },
        target_host: {
          ...target_host,
        },
        build_host: null,
      },
      {
        logging: { group: { name: machine, flake: { identifier: curr_uri } } },
      },
    ).promise.finally(() => {
      setIsUpdating(false);
    });
  };

  return (
    <>
      <div class="flex flex-col gap-6">
        <MachineActionsBar
          machineName={detailed.machine.name || ""}
          onInstall={() =>
            navigate(`/machines/${detailed.machine.name || ""}/install`)
          }
          onUpdate={handleUpdateButton}
          onCredentials={() =>
            navigate(`/machines/${detailed.machine.name || ""}/vars`)
          }
        />

        <div class="p-4">
          <span class="mb-2 flex w-full justify-center">
            <MachineAvatar name={detailed.machine.name || ""} />
          </span>

          <Form
            onSubmit={handleSubmit}
            class="mx-auto flex w-full max-w-2xl flex-col gap-y-6"
          >
            <MachineGeneralFields formStore={formStore} />
            <MachineHardwareInfo formStore={formStore} />

            <footer class="flex justify-end gap-y-3 border-t border-secondary-200 pt-5">
              <Button
                type="submit"
                disabled={formStore.submitting || !formStore.dirty}
              >
                Update edits
              </Button>
            </footer>
          </Form>
        </div>
      </div>
    </>
  );
}
