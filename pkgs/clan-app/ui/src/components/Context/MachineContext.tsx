import { Accessor, createContext, JSX, useContext } from "solid-js";
import { Machine } from "@/src/models/Machine";

const machineContext = createContext<Accessor<Machine>>();

export function useMachineContext() {
  return useContext(machineContext);
}

export function MachineContextProvider(props: {
  machine: Accessor<Machine>;
  children: JSX.Element;
}) {
  return (
    <machineContext.Provider value={props.machine}>
      {props.children}
    </machineContext.Provider>
  );
}
