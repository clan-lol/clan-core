// renderRoutes.ts
import { Route } from "@solidjs/router";
import type { JSXElement } from "solid-js";

export type AppRoute = {
  path: string;
  component?: () => JSXElement;
  children?: AppRoute[];
};

export function renderRoutes(routes: AppRoute[], parentPath = ""): JSXElement[] {
  return routes.map(({ path, component, children }) => {
    const fullPath = `${parentPath}/${path}`.replace(/\/+/g, "/");

    return (
        <Route path={path} component={component} key={fullPath}>
  {children && renderRoutes(children, fullPath)}
</Route>
    );
  });
}
