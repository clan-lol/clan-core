import { createSignal, createContext, useContext, JSXElement } from "solid-js";

const initialValue = 0 as const;
export const makeCountContext = () => {
  const [count, setCount] = createSignal(0);
  const [machines, setMachines] = createSignal<string[]>([]);
  const [loading, setLoading] = createSignal(false);

  // Add this callback to global window so we can test it from gtk
  // @ts-ignore
  window.clan.setMachines = (data: str) => {
    try {
      setMachines(JSON.parse(data));
    } catch (e) {
      alert(`Error parsing JSON: ${e}`);
    } finally {
      setLoading(false);
    }
  };

  return [
    { count, loading, machines },
    {
      setCount,
      setLoading,
      setMachines,
      getMachines: () => {
        // When the gtk function sends its data the loading state will be set to false
        setLoading(true);
        // Example of how to dispatch a gtk function
        // @ts-ignore
        window.webkit.messageHandlers.gtk.postMessage(1);
      },
    },
  ] as const;
  // `as const` forces tuple type inference
};
type CountContextType = ReturnType<typeof makeCountContext>;

export const CountContext = createContext<CountContextType>([
  { count: () => initialValue, loading: () => false, machines: () => [] },
  {
    setCount: () => {},
    setLoading: () => {},
    setMachines: () => {},
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
