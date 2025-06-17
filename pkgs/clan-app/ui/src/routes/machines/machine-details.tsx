import { callApi } from "@/src/api";
import { useParams } from "@solidjs/router";
import { useQuery } from "@tanstack/solid-query";
import { Show } from "solid-js";

import { Header } from "@/src/layout/header";
import { useClanContext } from "@/src/contexts/clan";
import { MachineForm } from "./components/MachineForm";

export const MachineDetails = () => {
  const params = useParams();
  const { activeClanURI } = useClanContext();

  const genericQuery = useQuery(() => ({
    queryKey: [activeClanURI(), "machine", params.id, "get_machine_details"],
    queryFn: async () => {
      const curr = activeClanURI();
      if (curr) {
        const result = await callApi("get_machine_details", {
          machine: {
            flake: {
              identifier: curr,
            },
            name: params.id,
          },
        }).promise;
        if (result.status === "error") throw new Error("Failed to fetch data");
        return result.data;
      }
    },
  }));

  return (
    <>
      <Header title={`${params.id} machine`} showBack />
      <Show
        when={genericQuery.data}
        fallback={<div class="p-4">Loading...</div>}
      >
        {(data) => <MachineForm detailed={data()} />}
      </Show>
    </>
  );
};
