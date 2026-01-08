import { createContext, FlowComponent, useContext } from "solid-js";
import { createSysStore, Sys, SysMethods } from ".";

const SysContext = createContext<readonly [Sys, SysMethods]>();

export function useSysContext(): readonly [Sys, SysMethods] {
  const value = useContext(SysContext);
  if (!value) {
    throw new Error("useSysContext must be used within a SysContextProvider");
  }
  return value;
}

export const SysContextProvider: FlowComponent = (props) => {
  return (
    <SysContext.Provider value={createSysStore()}>
      {props.children}
    </SysContext.Provider>
  );
};
