import { Component, JSXElement } from "solid-js";

interface LayoutProps {
  children: JSXElement;
}

export const Layout: Component<LayoutProps> = (props) => {
  return <div class="grid grid-cols-8">{props.children}</div>;
};
