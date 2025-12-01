import styles from "./Sidebar.module.css";
import { SidebarHeader } from "@/src/components/Sidebar/SidebarHeader";
import { SidebarBody } from "@/src/components/Sidebar/SidebarBody";
import cx from "classnames";
import { splitProps } from "solid-js";

interface LinkProps {
  path: string;
  label?: string;
}

interface SectionProps {
  title: string;
  links: LinkProps[];
}

export interface SidebarProps {
  class?: string;
  staticSections?: SectionProps[];
}

export default function Sidebar(props: SidebarProps) {
  const [bodyProps] = splitProps(props, ["staticSections"]);

  return (
    <div class={cx(styles.sidebar, props.class)}>
      <SidebarHeader />
      <SidebarBody {...bodyProps} />
    </div>
  );
}
