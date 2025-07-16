import { Component } from "solid-js";
import { RouteSectionProps, useNavigate } from "@solidjs/router";
import { activeClanURI } from "@/src/stores/clan";
import { navigateToClan } from "@/src/hooks/clan";

export const Layout: Component<RouteSectionProps> = (props) => {
  const navigate = useNavigate();

  // check for an active clan uri and redirect to it on first load
  const activeURI = activeClanURI();
  if (!props.location.pathname.startsWith("/clan/") && activeURI) {
    navigateToClan(navigate, activeURI);
  } else {
    navigate("/");
  }

  return <div class="size-full h-screen">{props.children}</div>;
};
