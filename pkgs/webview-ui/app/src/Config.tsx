import { createSignal, createContext, useContext, JSXElement } from "solid-js";
import { PYAPI } from "./message";

export const makeCountContext = () => {
  const [machines, setMachines] = createSignal<string[]>([]);
  const [loading, setLoading] = createSignal(false);

  PYAPI.list_machines.receive((machines) => {
    setLoading(false);
    setMachines(machines);
  });

  return [
    { loading, machines },
    {
      getMachines: () => {
        // When the gtk function sends its data the loading state will be set to false
        setLoading(true);
        PYAPI.list_machines.dispatch(null);
      },
    },
  ] as const;
  // `as const` forces tuple type inference
};
type CountContextType = ReturnType<typeof makeCountContext>;

export const CountContext = createContext<CountContextType>([
  { loading: () => false, machines: () => [] },
  {
    getMachines: () => {},
  },
]);

export const useCountContext = () => useContext(CountContext);

export function CountProvider(props: { children: JSXElement }) {
  return (
    <CountContext.Provider value={makeCountContext()}>
      {props.children}
    </CountContext.Provider>
  );
}
