import { Accessor, createContext, FlowComponent, useContext } from "solid-js";
import {
  Machine,
  MachineMethods,
  Machines,
  MachinesMethods,
  useClanContext,
  useClansContext,
} from "..";
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
  machines: Accessor<Machines>;
}> = (props) => {
  const clanValue = useClanContext();
  const clansValue = useClansContext();
  return (
    <MachinesContext.Provider
      value={createMachinesStore(props.machines, clanValue, clansValue)}
    >
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
  machine: Accessor<Machine>;
}> = (props) => {
  const machinesValue = useMachinesContext();
  const clanValue = useClanContext();
  const clansValue = useClansContext();
  return (
    <MachineContext.Provider
      value={createMachineStore(
        props.machine,
        machinesValue,
        clanValue,
        clansValue,
      )}
    >
      {props.children}
    </MachineContext.Provider>
  );
};
