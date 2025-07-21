import "./Sidebar.css";
import { SidebarHeader } from "@/src/components/Sidebar/SidebarHeader";
import { SidebarBody } from "@/src/components/Sidebar/SidebarBody";

export interface LinkProps {
  path: string;
  label?: string;
}

export interface SectionProps {
  title: string;
  links: LinkProps[];
}

export interface SidebarProps {
  staticSections?: SectionProps[];
}

export const Sidebar = (props: SidebarProps) => {
  return (
    <>
      <div class="sidebar">
        <SidebarHeader />
        <SidebarBody {...props} />
      </div>
    </>
  );
};
