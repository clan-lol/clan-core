import { createContext, JSX, useContext } from "solid-js";
import { Machine } from "./ClanContext/Machine";

const machineContext = createContext<Machine>();

export function useMachineContext() {
  return useContext(machineContext);
}

export function MachineContextProvider(props: {
  machine: Machine;
  children: JSX.Element;
}) {
  return (
    <machineContext.Provider value={props.machine}>
      {props.children}
    </machineContext.Provider>
  );
}
