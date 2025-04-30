import { A } from "@solidjs/router";
import { Typography } from "@/src/components/Typography";
import "./css/sidebar.css";

interface SidebarListItem {
  title: string;
  href: string;
}

export const SidebarListItem = (props: SidebarListItem) => {
  const { title, href } = props;

  return (
    <li class="">
      <A class="sidebar__list__link" href={href}>
        <Typography
          class="sidebar__list__content"
          tag="span"
          hierarchy="body"
          size="xs"
          weight="normal"
          color="primary"
          inverted={true}
        >
          {title}
        </Typography>
      </A>
    </li>
  );
};
