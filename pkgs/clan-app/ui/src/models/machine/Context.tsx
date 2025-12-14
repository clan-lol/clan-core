import { Accessor, createContext, FlowComponent, useContext } from "solid-js";
import { Machine, MachineMethods, Machines, MachinesMethods } from "..";
import { createMachineStore } from "./machine";
import { createMachinesStore } from "./machines";

const MachinesContext =
  createContext<readonly [Accessor<Machines>, MachinesMethods]>();

export function useMachinesContext(): readonly [
  Accessor<Machines>,
  MachinesMethods,
] {
  const value = useContext(MachinesContext);
  if (!value) {
    throw new Error(
      "useMachinesContext must be used within a MachinesContextProvider",
    );
  }
  return value;
}

export const MachinesContextProvider: FlowComponent<{
  value: Accessor<Machines>;
}> = (props) => {
  return (
    <MachinesContext.Provider value={createMachinesStore(props.value)}>
      {props.children}
    </MachinesContext.Provider>
  );
};

const MachineContext =
  createContext<readonly [Accessor<Machine>, MachineMethods]>();

export function useMachineContext(): readonly [
  Accessor<Machine>,
  MachineMethods,
] {
  const value = useContext(MachineContext);
  if (!value) {
    throw new Error(
      "useMachineContext must be used within a MachineContextProvider",
    );
  }
  return value;
}

export const MachineContextProvider: FlowComponent<{
  value: Accessor<Machine>;
}> = (props) => {
  return (
    <MachineContext.Provider value={createMachineStore(props.value)}>
      {props.children}
    </MachineContext.Provider>
  );
};
