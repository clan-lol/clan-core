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
import Icon, { IconVariant } from "../icon";

export const SidebarSection = (props: {
  title: string;
  icon: IconVariant;
  children: JSX.Element;
}) => {
  const { title, children } = props;

  return (
    <details class="sidebar__section accordeon" open>
      <summary class="accordeon__header">
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
