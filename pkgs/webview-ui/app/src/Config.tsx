import {
  createSignal,
  createContext,
  useContext,
  JSXElement,
  createEffect,
} from "solid-js";
import { OperationResponse, pyApi } from "./message";

export const makeCountContext = () => {
  const [machines, setMachines] = createSignal<
    OperationResponse<"list_machines">
  >([]);
  const [loading, setLoading] = createSignal(false);

  pyApi.list_machines.receive((machines) => {
    setLoading(false);
    setMachines(machines);
  });

  createEffect(() => {
    console.log("The count is now", machines());
  });

  return [
    { loading, machines },
    {
      getMachines: () => {
        // When the gtk function sends its data the loading state will be set to false
        setLoading(true);
        pyApi.list_machines.dispatch({ debug: true, flake_url: "." });
      },
    },
  ] as const;
  // `as const` forces tuple type inference
};
type CountContextType = ReturnType<typeof makeCountContext>;

export const CountContext = createContext<CountContextType>([
  {
    loading: () => false,

    // eslint-disable-next-line
    machines: () => ([]),
  },
  {
    // eslint-disable-next-line
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
