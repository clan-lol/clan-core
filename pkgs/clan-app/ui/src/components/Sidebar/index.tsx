import styles from "./Sidebar.module.css";
import SidebarHeader from "@/src/components/Sidebar/SidebarHeader";
import SidebarBody from "@/src/components/Sidebar/SidebarBody";

export default function Sidebar() {
  return (
    <div class={styles.sidebar}>
      <SidebarHeader />
      {/* <SidebarBody /> */}
    </div>
  );
}
