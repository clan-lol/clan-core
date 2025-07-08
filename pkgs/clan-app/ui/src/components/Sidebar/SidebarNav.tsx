import "./SidebarNav.css";
import { SidebarNavHeader } from "@/src/components/Sidebar/SidebarNavHeader";
import { SidebarNavBody } from "@/src/components/Sidebar/SidebarNavBody";
import { MachineStatus } from "@/src/components/MachineStatus/MachineStatus";

export interface LinkProps {
  path: string;
  label?: string;
}

export interface SectionProps {
  label: string;
  links: LinkProps[];
}

export interface MachineProps {
  label: string;
  path: string;
  status: MachineStatus;
  serviceCount: number;
}

export interface ClanLinkProps {
  label: string;
  path: string;
}

export interface ClanProps {
  label: string;
  settingsPath: string;
  machines: MachineProps[];
}

export interface SidebarNavProps {
  clanDetail: ClanProps;
  clanLinks: ClanLinkProps[];
  extraSections: SectionProps[];
}

export const SidebarNav = (props: SidebarNavProps) => {
  return (
    <div class="sidebar">
      <SidebarNavHeader {...props} />
      <SidebarNavBody {...props} />
    </div>
  );
};
