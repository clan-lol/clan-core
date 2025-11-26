import { Show, Suspense } from "solid-js";
import { useClanContext } from "./contexts/ClanContext";
import { Onboarding } from "./components/Onboarding";
import Workspace from "./components/Workspace";
import Splash from "./scene/splash";

export default function Entrypoint() {
  const { clans } = useClanContext()!;
  return (
    <Suspense fallback={<Splash />}>
      <Show when={clans()?.active} fallback={<Onboarding />}>
        <Workspace />
      </Show>
    </Suspense>
  );
}
