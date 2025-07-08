import { RouteSectionProps, useParams } from "@solidjs/router";
import { Component } from "solid-js";
import { clanURIParam } from "@/src/hooks/clan";
import { CubeScene } from "@/src/scene/cubes";

export const Clan: Component<RouteSectionProps> = (props) => {
  const params = useParams();
  const clanURI = clanURIParam(params);
  return <CubeScene />;
};
