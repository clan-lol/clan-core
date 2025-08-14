import styles from "./Sidebar.module.css";
import { SidebarHeader } from "@/src/components/Sidebar/SidebarHeader";
import { SidebarBody } from "@/src/components/Sidebar/SidebarBody";
import cx from "classnames";

export interface LinkProps {
  path: string;
  label?: string;
}

export interface SectionProps {
  title: string;
  links: LinkProps[];
}

export interface SidebarProps {
  class?: string;
  staticSections?: SectionProps[];
}

export const Sidebar = (props: SidebarProps) => {
  return (
    <div class={cx(styles.sidebar, props.class)}>
      <SidebarHeader />
      <SidebarBody class={cx(styles.body)} {...props} />
    </div>
  );
};
