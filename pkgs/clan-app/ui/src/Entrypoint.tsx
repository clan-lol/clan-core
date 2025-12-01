import { Show, Suspense } from "solid-js";
import { Onboarding } from "./components/Onboarding";
import Workspace from "./components/Workspace";
import Splash from "./scene/splash";
import { ClanContextProvider } from "./components/Context/ClanContext";
import { createAsync } from "@solidjs/router";
import { ClanList } from "./models/Clan";
import { ClansContextProvider } from "./components/Context/ClansContext";

export default function Entrypoint() {
  const clans = createAsync(async () => await ClanList.get());
  return (
    <Suspense fallback={<Splash />}>
      <ClansContextProvider clans={clans}>
        <Show when={clans()?.active} fallback={<Onboarding />}>
          <ClanContextProvider clan={() => clans()!.active!}>
            <Workspace />
          </ClanContextProvider>
        </Show>
      </ClansContextProvider>
    </Suspense>
  );
}
