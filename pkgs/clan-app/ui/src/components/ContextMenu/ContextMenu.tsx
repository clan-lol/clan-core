import { onCleanup, onMount } from "solid-js";
import styles from "./ContextMenu.module.css";
import { Typography } from "../Typography/Typography";

export const Menu = (props: {
  x: number;
  y: number;
  onSelect: (option: "move") => void;
  close: () => void;
  intersect: string[];
}) => {
  let ref: HTMLUListElement;

  const handleClickOutside = (e: MouseEvent) => {
    if (!ref.contains(e.target as Node)) {
      props.close();
    }
  };

  onMount(() => {
    document.addEventListener("mousedown", handleClickOutside);
  });

  onCleanup(() =>
    document.removeEventListener("mousedown", handleClickOutside),
  );
  const currentMachine = () => props.intersect.at(0) || null;

  return (
    <ul
      ref={(el) => (ref = el)}
      style={{
        position: "absolute",
        top: `${props.y}px`,
        left: `${props.x}px`,
        "z-index": 1000,
        "pointer-events": "auto",
      }}
      class={styles.list}
      onContextMenu={(e) => {
        // Prevent default context menu
        e.preventDefault();
        e.stopPropagation();
      }}
    >
      <li
        class={styles.item}
        aria-disabled={!currentMachine()}
        onClick={() => {
          console.log("Move clicked", currentMachine());
          props.onSelect("move");
          props.close();
        }}
      >
        <Typography
          hierarchy="label"
          size="s"
          weight="bold"
          color={currentMachine() ? "primary" : "quaternary"}
        >
          Move
        </Typography>
      </li>
    </ul>
  );
};
