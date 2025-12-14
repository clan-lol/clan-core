import { Accessor, createContext, FlowComponent, useContext } from "solid-js";
import {
  ServiceInstance,
  ServiceInstanceMethods,
  ServiceInstances,
  ServiceInstancesMethods,
} from "..";
import { createServiceInstancesStore } from "./instances";
import { createServiceInstanceStore } from "./instance";

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
  return (
    <ServiceInstancesContext.Provider
      value={createServiceInstancesStore(props.value)}
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
      value={createServiceInstanceStore(props.value)}
    >
      {props.children}
    </ServiceInstanceContext.Provider>
  );
};
