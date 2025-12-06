import { Accessor, Component, createContext, JSX, useContext } from "solid-js";
import {
  createMachinesStore,
  createMachineStore,
  Machine,
  Machines,
  MachineSetters,
  MachinesSetters,
} from "@/src/models";
import { useClanContext, useClansContext } from "./ClanContext";

const MachinesContext = createContext<[Accessor<Machines>, MachinesSetters]>();

export function useMachinesContext(): [Accessor<Machines>, MachinesSetters] {
  const value = useContext(MachinesContext);
  if (!value) {
    throw new Error(
      "useMachinesContext must be used within a MachinesContextProvider",
    );
  }
  return value;
}

export const MachinesContextProvider: Component<{
  machines: Accessor<Machines>;
  children: JSX.Element;
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

const MachineContext = createContext<[Accessor<Machine>, MachineSetters]>();

export function useMachineContext(): [Accessor<Machine>, MachineSetters] {
  const value = useContext(MachineContext);
  if (!value) {
    throw new Error(
      "useMachineContext must be used within a MachineContextProvider",
    );
  }
  return value;
}

export const MachineContextProvider: Component<{
  machine: Accessor<Machine>;
  children: JSX.Element;
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
