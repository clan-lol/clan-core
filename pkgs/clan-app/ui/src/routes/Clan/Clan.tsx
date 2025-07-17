import { RouteSectionProps } from "@solidjs/router";
import { Component, JSX } from "solid-js";
import { useMaybeClanURI } from "@/src/hooks/clan";
import { CubeScene } from "@/src/scene/cubes";
import { MachinesQueryResult, useMachinesQuery } from "@/src/queries/queries";

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

const SceneDataProvider = (props: {
  clanURI: string | null;
  children: (sceneData: { query: MachinesQueryResult }) => JSX.Element;
}) => {
  const machinesQuery = useMachinesQuery({ clanURI: props.clanURI });

  // This component can be used to provide scene data or context if needed
  return props.children({ query: machinesQuery });
};
