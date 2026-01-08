import {
  Accessor,
  createContext,
  createEffect,
  FlowComponent,
  on,
  useContext,
} from "solid-js";
import {
  ServiceInstance,
  ServiceInstanceMethods,
  ServiceInstances,
  ServiceInstancesMethods,
  useClanContext,
  useClansContext,
  useUIContext,
} from "..";
import { createInstancesMethods } from "./instances";
import { createInstanceMethods } from "./instance";

const ServiceInstancesContext =
  createContext<
    readonly [Accessor<ServiceInstances>, ServiceInstancesMethods]
  >();

export function useServiceInstancesContext(): readonly [
  Accessor<ServiceInstances>,
  ServiceInstancesMethods,
] {
  const value = useContext(ServiceInstancesContext);
  if (!value) {
    throw new Error(
      "useServiceInstancesContext must be used within a ServiceInstancesContextProvider",
    );
  }
  return value;
}

export const ServiceInstancesContextProvider: FlowComponent<{
  value: Accessor<ServiceInstances>;
}> = (props) => {
  const [, { setToolbarMode }] = useUIContext();
  createEffect(
    on(
      () => props.value().activeServiceInstance,
      (instance) => {
        if (instance) {
          setToolbarMode({ type: "service" });
        } else {
          setToolbarMode({ type: "select" });
        }
      },
      { defer: true },
    ),
  );

  return (
    <ServiceInstancesContext.Provider
      value={[
        props.value,
        createInstancesMethods(
          props.value,
          useClanContext(),
          useClansContext(),
        ),
      ]}
    >
      {props.children}
    </ServiceInstancesContext.Provider>
  );
};

const ServiceInstanceContext =
  createContext<readonly [Accessor<ServiceInstance>, ServiceInstanceMethods]>();

export function useServiceInstanceContext(): readonly [
  Accessor<ServiceInstance>,
  ServiceInstanceMethods,
] {
  const value = useContext(ServiceInstanceContext);
  if (!value) {
    throw new Error(
      "useServiceInstanceContext must be used within a ServiceInstanceContextProvider",
    );
  }
  return value;
}

export const ServiceInstanceContextProvider: FlowComponent<{
  value: Accessor<ServiceInstance>;
}> = (props) => {
  return (
    <ServiceInstanceContext.Provider
      value={[
        props.value,
        createInstanceMethods(
          props.value,
          useServiceInstancesContext(),
          useClanContext(),
          useClansContext(),
        ),
      ]}
    >
      {props.children}
    </ServiceInstanceContext.Provider>
  );
};
