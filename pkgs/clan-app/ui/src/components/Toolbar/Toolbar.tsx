import "./Toolbar.css";
import { JSX } from "solid-js";

export interface ToolbarProps {
  children: JSX.Element;
}

export const Toolbar = (props: ToolbarProps) => {
  return (
    <div class="toolbar" role="toolbar" aria-orientation="horizontal">
      {props.children}
    </div>
  );
};
