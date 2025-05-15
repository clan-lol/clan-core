import { Component, createEffect } from "solid-js";
import { Sidebar } from "@/src/components/Sidebar";
import { clanList } from "../App";
import { RouteSectionProps, useNavigate } from "@solidjs/router";

export const Layout: Component<RouteSectionProps> = (props) => {
  const navigate = useNavigate();
  createEffect(() => {
    console.log(
      "empty ClanList, redirect to welcome page",
      clanList().length === 0,
    );
    if (clanList().length === 0) {
      navigate("/welcome");
    }
  });

  return (
    <div class="h-screen w-full p-4 bg-def-2">
      <div class="flex size-full flex-row-reverse">
        <div class="my-2 ml-8 flex-1 overflow-x-hidden overflow-y-scroll rounded-lg border bg-def-1 border-def-3">
          {props.children}
        </div>
        <Sidebar {...props} />
      </div>
    </div>
  );
};
