import { For, createEffect, Show, type JSX, children } from "solid-js";
import { A, RouteSectionProps } from "@solidjs/router";
import { activeURI } from "@/src/App";
import { createQuery } from "@tanstack/solid-query";
import { callApi } from "@/src/api";
import { AppRoute, routes } from "@/src/index";
import { SidebarHeader } from "./SidebarHeader";
import { SidebarListItem } from "./SidebarListItem";
import { Typography } from "../Typography";
import "./css/sidebar.css";

export const SidebarSection = (props: {
  title: string;
  children: JSX.Element;
}) => {
  const { title, children } = props;

  return (
    <details class="sidebar__section accordeon" open>
      <summary class="accordeon__header">
        <Typography
          class="uppercase"
          tag="p"
          hierarchy="body"
          size="xs"
          weight="normal"
          color="tertiary"
          inverted={true}
        >
          {title}
        </Typography>
      </summary>
      <div class="accordeon__body">{children}</div>
    </details>
  );
};

export const Sidebar = (props: RouteSectionProps) => {
  createEffect(() => {
    console.log("machines");
    console.log(routes);
  });

  const query = createQuery(() => ({
    queryKey: [activeURI(), "meta"],
    queryFn: async () => {
      const curr = activeURI();
      if (curr) {
        const result = await callApi("show_clan_meta", { uri: curr });
        console.log("refetched meta for ", curr);
        if (result.status === "error") throw new Error("Failed to fetch data");

        return result.data;
      }
    },
  }));

  return (
    <div class="sidebar opacity-95">
      <Show
        when={query.data}
        fallback={<SidebarHeader clanName={"Untitled"} />}
      >
        {(meta) => <SidebarHeader clanName={meta().name} />}
      </Show>
      <div class="sidebar__body max-h-[calc(100vh-4rem)] overflow-scroll">
        <For each={routes.filter((r) => !r.hidden && r.path != "/clans")}>
          {(route: AppRoute) => (
            <Show
              when={route.children}
              fallback={
                <SidebarListItem href={route.path} title={route.label} />
              }
            >
              {(children) => (
                <SidebarSection title={route.label}>
                  <ul>
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
