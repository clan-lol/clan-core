import "./Loader.css";
import cx from "classnames";

export type Hierarchy = "primary" | "secondary";

export interface LoaderProps {
  hierarchy?: Hierarchy;
}

export const Loader = (props: LoaderProps) => {
  return (
    <div class={cx("loader", props.hierarchy || "primary")}>
      <div class="wrapper">
        <div class="parent"></div>
      </div>
      <div class="child"></div>
    </div>
  );
};
