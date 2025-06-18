import { For, type JSX, Show } from "solid-js";
import { RouteSectionProps } from "@solidjs/router";
import { AppRoute, routes } from "@/src";
import { SidebarHeader } from "./SidebarHeader";
import { SidebarListItem } from "./SidebarListItem";
import { Typography } from "../Typography";
import "./css/sidebar.css";
import Icon, { IconVariant } from "../icon";
import { clanMetaQuery } from "@/src/queries/clan-meta";

export const SidebarSection = (props: {
  title: string;
  icon: IconVariant;
  children: JSX.Element;
}) => {
  const { title, children } = props;

  return (
    <details class="sidebar__section accordeon" open>
      <summary style="display: contents;">
        <div class="accordeon__header">
          <Typography
            class="inline-flex w-full gap-2 uppercase !tracking-wider"
            tag="p"
            hierarchy="body"
            size="xxs"
            weight="normal"
            color="tertiary"
            inverted={true}
          >
            <Icon class="opacity-90" icon={props.icon} size={13} />
            {title}
            <Icon icon="CaretDown" class="ml-auto" size={10} />
          </Typography>
        </div>
      </summary>
      <div class="accordeon__body">{children}</div>
    </details>
  );
};

export const Sidebar = (props: RouteSectionProps) => {
  const query = clanMetaQuery();

  return (
    <div class="sidebar">
      <Show
        when={query.data}
        fallback={<SidebarHeader clanName={"Untitled"} />}
      >
        {(meta) => <SidebarHeader clanName={meta().name} />}
      </Show>
      <div class="sidebar__body max-h-[calc(100vh-4rem)] overflow-scroll">
        <For each={routes.filter((r) => !r.hidden)}>
          {(route: AppRoute) => (
            <Show
              when={route.children}
              fallback={
                <SidebarListItem href={route.path} title={route.label} />
              }
            >
              {(children) => (
                <SidebarSection
                  title={route.label}
                  icon={route.icon || "Paperclip"}
                >
                  <ul class="flex flex-col gap-y-0.5">
                    <For each={children().filter((r) => !r.hidden)}>
                      {(child) => (
                        <SidebarListItem
                          href={`${route.path}${child.path}`}
                          title={child.label}
                        />
                      )}
                    </For>
                  </ul>
                </SidebarSection>
              )}
            </Show>
          )}
        </For>
      </div>
    </div>
  );
};
