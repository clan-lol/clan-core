import { Component } from "solid-js";
import { RouteSectionProps } from "@solidjs/router";

export const Layout: Component<RouteSectionProps> = (props) => (
  <div class="size-full h-screen">{props.children}</div>
);
