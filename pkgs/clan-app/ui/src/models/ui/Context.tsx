import { createContext, FlowComponent, useContext } from "solid-js";
import { createUIStore, UI, UIMethods } from ".";

const UIContext = createContext<readonly [UI, UIMethods]>();

export function useUIContext(): readonly [UI, UIMethods] {
  const value = useContext(UIContext);
  if (!value) {
    throw new Error("useUIContext must be used within a UIContextProvider");
  }
  return value;
}

export const UIContextProvider: FlowComponent = (props) => {
  return (
    <UIContext.Provider value={createUIStore()}>
      {props.children}
    </UIContext.Provider>
  );
};
