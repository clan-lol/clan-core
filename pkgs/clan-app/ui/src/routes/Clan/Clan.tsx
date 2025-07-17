import { RouteSectionProps } from "@solidjs/router";
import { Component, JSX } from "solid-js";
import { useMaybeClanURI } from "@/src/hooks/clan";
import { CubeScene } from "@/src/scene/cubes";
import { useQuery, UseQueryResult } from "@tanstack/solid-query";
import { callApi, SuccessData } from "@/src/hooks/api";

export const Clans: Component<RouteSectionProps> = (props) => {
  return (
    <>
      <div
        style={{
          position: "absolute",
          top: 0,
        }}
      >
        {props.children}
      </div>
      <ClanSwitchDog />
    </>
  );
};

const ClanSwitchDog = () => {
  const maybeClanURI = useMaybeClanURI();

  return (
    <SceneDataProvider clanURI={maybeClanURI}>
      {({ query }) => <CubeScene cubesQuery={query} />}
    </SceneDataProvider>
  );
};

export type ListMachines = SuccessData<"list_machines">;

const SceneDataProvider = (props: {
  clanURI: string | null;
  children: (sceneData: { query: UseQueryResult<ListMachines> }) => JSX.Element;
}) => {
  const machinesQuery = useQuery<ListMachines>(() => ({
    queryKey: ["clans", props.clanURI, "machines"],
    enabled: !!props.clanURI,
    queryFn: async () => {
      if (!props.clanURI) {
        return {};
      }
      const api = callApi("list_machines", {
        flake: {
          identifier: props.clanURI,
        },
      });
      const result = await api.result;
      if (result.status === "error") {
        console.error("Error fetching machines:", result.errors);
        return {};
      }
      return result.data;
    },
  }));

  // This component can be used to provide scene data or context if needed
  return props.children({ query: machinesQuery });
};
