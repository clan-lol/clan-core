import { JSX } from "solid-js";
import styles from "./Toolbar.module.css";

interface ToolbarProps {
  children: JSX.Element;
}

export const Toolbar = (props: ToolbarProps) => {
  return (
    <div class={styles.toolbar} role="toolbar" aria-orientation="horizontal">
      {props.children}
    </div>
  );
};
