import { RouteSectionProps } from "@solidjs/router";
import { maybeUseIdParam, useInputParam, useNameParam } from "@/src/hooks/clan";
import { createEffect } from "solid-js";
import { useClanContext } from "@/src/routes/Clan/Clan";

export const Service = (props: RouteSectionProps) => {
  const ctx = useClanContext();

  console.log("service route");

  createEffect(() => {
    const input = useInputParam();
    const name = useNameParam();
    const id = maybeUseIdParam();

    ctx.setWorldMode("service");

    console.log("service", input, name, id);
  });

  return <>h1</>;
};
