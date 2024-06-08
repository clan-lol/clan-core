import {
  createSignal,
  createContext,
  useContext,
  JSXElement,
  createEffect,
} from "solid-js";
import { OperationResponse, pyApi } from "./api";

export const makeMachineContext = () => {
  const [machines, setMachines] =
    createSignal<OperationResponse<"list_machines">>();
  const [loading, setLoading] = createSignal(false);

  pyApi.list_machines.receive((machines) => {
    setLoading(false);
    setMachines(machines);
  });

  createEffect(() => {
    console.log("The state is now", machines());
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
type MachineContextType = ReturnType<typeof makeMachineContext>;

export const MachineContext = createContext<MachineContextType>([
  {
    loading: () => false,

    // eslint-disable-next-line
    machines: () => undefined,
  },
  {
    // eslint-disable-next-line
    getMachines: () => {},
  },
]);

export const useMachineContext = () => useContext(MachineContext);

export function MachineProvider(props: { children: JSXElement }) {
  return (
    <MachineContext.Provider value={makeMachineContext()}>
      {props.children}
    </MachineContext.Provider>
  );
}
