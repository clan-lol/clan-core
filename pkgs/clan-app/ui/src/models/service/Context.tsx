import { Accessor, createContext, FlowComponent, useContext } from "solid-js";
import {
  ServiceInstance,
  ServiceInstanceMethods,
  ServiceInstances,
  ServiceInstancesMethods,
  useClanContext,
  useClansContext,
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
  serviceInstances: Accessor<ServiceInstances>;
}> = (props) => {
  const clanValue = useClanContext();
  const clansValue = useClansContext();
  return (
    <ServiceInstancesContext.Provider
      value={createServiceInstancesStore(
        props.serviceInstances,
        clanValue,
        clansValue,
      )}
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
  serviceInstance: Accessor<ServiceInstance>;
}> = (props) => {
  const instancesValue = useServiceInstancesContext();
  const clanValue = useClanContext();
  const clansValue = useClansContext();
  return (
    <ServiceInstanceContext.Provider
      value={createServiceInstanceStore(
        props.serviceInstance,
        instancesValue,
        clanValue,
        clansValue,
      )}
    >
      {props.children}
    </ServiceInstanceContext.Provider>
  );
};
