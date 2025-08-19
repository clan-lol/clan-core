import { Component, createEffect, on } from "solid-js";
import { RouteSectionProps, useNavigate } from "@solidjs/router";
import { activeClanURI } from "@/src/stores/clan";
import { navigateToClan } from "@/src/hooks/clan";

export const Layout: Component<RouteSectionProps> = (props) => {
  const navigate = useNavigate();

  // check for an active clan uri and redirect if no clan is active
  createEffect(
    on(activeClanURI, (activeURI) => {
      console.debug("Active Clan URI changed:", activeURI);
      if (activeURI && !props.location.pathname.startsWith("/clans/")) {
        navigateToClan(navigate, activeURI);
      } else {
        navigate("/");
      }
    }),
  );

  return <div class="size-full h-screen">{props.children}</div>;
};
