import { Accessor, Component, ErrorBoundary, Show, Suspense } from "solid-js";
import Onboarding from "./components/Onboarding";
import Workspace from "./components/Workspace";
import Splash from "./scene/splash";
import {
  ClansEntity,
  createClanStore,
  createClansStore,
  initClans,
} from "./models";
import {
  ClanContextProvider,
  ClansContextProvider,
  useClansContext,
} from "./components/Context/ClanContext";
import { createAsync } from "@solidjs/router";

const Entrypoint: Component = () => {
  const clans = createAsync(async () => await initClans());
  // Add other top level models here
  // const foo = createAsync(async () => await initFoo());
  return (
    <ErrorBoundary
      fallback={(error, reset) => {
        return (
          <div>
            <p>{error.message}</p>
            <button onClick={reset}>Try Again</button>
          </div>
        );
      }}
    >
      <Suspense fallback={<Splash />}>
        <Show when={clans() /* && foo() */}>
          <ClansContextProvider
            value={createClansStore(clans as Accessor<ClansEntity>)}
          >
            <Content />
          </ClansContextProvider>
        </Show>
      </Suspense>
    </ErrorBoundary>
  );
};
export default Entrypoint;

const Content: Component = () => {
  const [clans, clansSetters] = useClansContext();
  return (
    <Show when={clans.activeClan} fallback={<Onboarding />}>
      {(clan) => (
        <ClanContextProvider
          value={createClanStore(clan, [clans, clansSetters])}
        >
          <Workspace />
        </ClanContextProvider>
      )}
    </Show>
  );
};
