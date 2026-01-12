import { Accessor, Component, ErrorBoundary, Show, Suspense } from "solid-js";
import { createAsync } from "@solidjs/router";
import Onboarding from "./components/Onboarding";
import Workspace from "./components/Workspace";
import Splash from "./components/Splash";
import {
  ClanContextProvider,
  ClansContextProvider,
  ClansEntity,
  initClans,
  MachinesContextProvider,
  ServiceInstancesContextProvider,
  useClansContext,
} from "./models";
import { UIContextProvider } from "./models/ui";
import Modal from "./components/Modal";
import { SysContextProvider } from "./models/sys";

const Entrypoint: Component = () => {
  const clans = createAsync(async () => await initClans());
  // Add other top level models here
  // const foo = createAsync(async () => await initFoo());
  return (
    <ErrorBoundary
      fallback={(err: Error, reset) => {
        console.error(err);
        return (
          <div>
            <p>{err.message}</p>
            <button onClick={reset}>Try Again</button>
          </div>
        );
      }}
    >
      <SysContextProvider>
        <UIContextProvider>
          <Suspense fallback={<Splash />}>
            <Show when={clans() /* && foo() */}>
              <ClansContextProvider value={clans as Accessor<ClansEntity>}>
                <Content />
              </ClansContextProvider>
            </Show>
          </Suspense>
        </UIContextProvider>
      </SysContextProvider>
    </ErrorBoundary>
  );
};
export default Entrypoint;

const Content: Component = () => {
  const [clans] = useClansContext();
  return (
    <Show
      when={clans.activeClan}
      fallback={
        <>
          <Onboarding />
          <Modal />
        </>
      }
    >
      {(clan) => (
        <ClanContextProvider value={clan}>
          <MachinesContextProvider value={() => clan().machines}>
            <ServiceInstancesContextProvider
              value={() => clan().serviceInstances}
            >
              <Workspace />
              <Modal />
            </ServiceInstancesContextProvider>
          </MachinesContextProvider>
        </ClanContextProvider>
      )}
    </Show>
  );
};
