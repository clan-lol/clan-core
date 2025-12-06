import { Accessor, Component, ErrorBoundary, Show, Suspense } from "solid-js";
import Onboarding from "./components/Onboarding";
import Workspace from "./components/Workspace";
import Splash from "./scene/splash";
import { ClansEntity, initClans } from "./models";
import {
  ClanContextProvider,
  ClansContextProvider,
  useClansContext,
} from "./components/Context/ClanContext";
import { createAsync } from "@solidjs/router";
import { MachinesContextProvider } from "./components/Context/MachineContext";

const Entrypoint: Component = () => {
  const clans = createAsync(async () => await initClans());
  // Add other top level models here
  // const foo = createAsync(async () => await initFoo());
  return (
    <ErrorBoundary
      fallback={(err, reset) => {
        console.error(err);
        return (
          <div>
            <p>{err.message}</p>
            <button onClick={reset}>Try Again</button>
          </div>
        );
      }}
    >
      <Suspense fallback={<Splash />}>
        <Show when={clans() /* && foo() */}>
          <ClansContextProvider clans={clans as Accessor<ClansEntity>}>
            <Content />
          </ClansContextProvider>
        </Show>
      </Suspense>
    </ErrorBoundary>
  );
};
export default Entrypoint;

const Content: Component = () => {
  const [clans] = useClansContext();
  return (
    <Show when={clans.activeClan} fallback={<Onboarding />}>
      {(clan) => (
        <ClanContextProvider clan={clan}>
          <MachinesContextProvider machines={() => clan().machines}>
            <Workspace />
          </MachinesContextProvider>
        </ClanContextProvider>
      )}
    </Show>
  );
};
