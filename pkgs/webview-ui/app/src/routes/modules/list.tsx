import { SuccessData } from "@/src/api";
import { activeURI } from "@/src/App";
import { Button } from "@/src/components/button";
import { Header } from "@/src/layout/header";
import { createModulesQuery } from "@/src/queries";
import { A, useNavigate } from "@solidjs/router";
import { createSignal, For, Match, Switch } from "solid-js";
import { Typography } from "@/src/components/Typography";
import { Menu } from "@/src/components/Menu";
import { makePersisted } from "@solid-primitives/storage";
import { useQueryClient } from "@tanstack/solid-query";
import cx from "classnames";
import Icon from "@/src/components/icon";

export type ModuleInfo = SuccessData<"list_modules">["localModules"][string];

interface CategoryProps {
  categories: string[];
}
const Categories = (props: CategoryProps) => {
  return (
    <span class="inline-flex h-full align-middle">
      {props.categories.map((category) => (
        <span class="text-sm font-normal">{category}</span>
      ))}
    </span>
  );
};

interface RolesProps {
  roles: Record<string, null>;
}
const Roles = (props: RolesProps) => {
  return (
    <div class="flex flex-wrap items-center gap-2">
      <span>
        <Typography hierarchy="body" size="xs">
          Service
        </Typography>
      </span>
      {Object.keys(props.roles).map((role) => (
        <span class="">{role}</span>
      ))}
    </div>
  );
};

const ModuleItem = (props: {
  name: string;
  info: ModuleInfo;
  class?: string;
}) => {
  const { name, info } = props;
  const navigate = useNavigate();

  return (
    <div
      class={cx(
        "col-span-1 flex flex-col gap-3 border-b border-secondary-200 pb-4",
        props.class,
      )}
    >
      {/* <div class="stat-figure text-primary-800">
        <div class="join">
          <Menu popoverid={`menu-${props.name}`} label={<Icon icon={"More"} />}>
            <ul class="z-[1] w-52 p-2 shadow">
              <li>
                <a
                  onClick={() => {
                    navigate(`/modules/details/${name}`);
                  }}
                >
                  Configure
                </a>
              </li>
            </ul>
          </Menu>
        </div>
      </div> */}

      <header class="flex flex-col gap-4">
        <A href={`/modules/details/${name}`}>
          <div class="">
            <div class="flex flex-col">
              {/* <Categories categories={info.categories} /> */}
              <Typography hierarchy="title" size="m" weight="medium">
                {name}
              </Typography>
            </div>
          </div>
        </A>

        <div class="w-full">
          <Typography hierarchy="body" size="xs">
            description
            {/* TODO: {info.description} */}
          </Typography>
        </div>
      </header>
      <Roles roles={info.roles || {}} />
    </div>
  );
};

export const ModuleList = () => {
  const queryClient = useQueryClient();
  const modulesQuery = createModulesQuery(activeURI(), {
    features: ["inventory"],
  });

  const [view, setView] = makePersisted(createSignal<"list" | "grid">("list"), {
    name: "modules_view",
    storage: localStorage,
  });

  const refresh = async () => {
    queryClient.invalidateQueries({
      // Invalidates the cache for of all types of machine list at once
      queryKey: [activeURI(), "list_modules"],
    });
  };
  return (
    <>
      <Header
        title="App Store"
        toolbar={
          <>
            <Button
              variant="light"
              size="s"
              onClick={() => refresh()}
              startIcon={<Icon icon="Update" />}
            />

            <div class="button-group">
              <Button
                onclick={() => setView("list")}
                variant={view() == "list" ? "dark" : "light"}
                size="s"
                startIcon={<Icon icon="List" />}
              />

              <Button
                onclick={() => setView("grid")}
                variant={view() == "grid" ? "dark" : "light"}
                size="s"
                startIcon={<Icon icon="Grid" />}
              />
            </div>
            <span class="" data-tip="New Machine">
              <Button
                size="s"
                variant="light"
                startIcon={<Icon size={14} icon="CaretUp" />}
              >
                Import Module
              </Button>
            </span>
          </>
        }
      />
      <Switch fallback="Error">
        <Match when={modulesQuery.isFetching}>Loading....</Match>
        <Match when={modulesQuery.data}>
          {(modules) => (
            <div
              class="grid gap-6 p-6"
              classList={{
                "grid-cols-1": view() === "list",
                "grid-cols-2": view() === "grid",
              }}
            >
              <For each={Object.entries(modules().modulesPerSource)}>
                {([sourceName, v]) => (
                  <>
                    <div>
                      <Typography size="default" hierarchy="label">
                        {sourceName}
                      </Typography>
                    </div>
                    <For each={Object.entries(v)}>
                      {([moduleName, moduleInfo]) => (
                        <ModuleItem
                          info={moduleInfo}
                          name={moduleName}
                          class={view() == "grid" ? cx("max-w-md") : ""}
                        />
                      )}
                    </For>
                  </>
                )}
              </For>
              <div>{"localModules"}</div>
              <For each={Object.entries(modules().localModules)}>
                {([moduleName, moduleInfo]) => (
                  <ModuleItem
                    info={moduleInfo}
                    name={moduleName}
                    class={view() == "grid" ? cx("max-w-md") : ""}
                  />
                )}
              </For>
            </div>
          )}
        </Match>
      </Switch>
    </>
  );
};
