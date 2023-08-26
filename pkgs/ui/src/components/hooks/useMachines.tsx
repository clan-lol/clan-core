import { useListMachines } from "@/api/default/default";
import { Machine, MachinesResponse } from "@/api/model";
import { AxiosError, AxiosResponse } from "axios";
import React, {
  createContext,
  Dispatch,
  ReactNode,
  SetStateAction,
  useMemo,
  useState,
} from "react";
import { KeyedMutator } from "swr";

type Filter = {
  name: keyof Machine;
  value: Machine[keyof Machine];
};
type Filters = Filter[];

type MachineContextType =
  | {
      rawData: AxiosResponse<MachinesResponse, any> | undefined;
      data: Machine[];
      isLoading: boolean;
      error: AxiosError<any> | undefined;
      isValidating: boolean;

      filters: Filters;
      setFilters: Dispatch<SetStateAction<Filters>>;
      mutate: KeyedMutator<AxiosResponse<MachinesResponse, any>>;
      swrKey: string | false | Record<any, any>;
    }
  | {
      isLoading: true;
      data: readonly [];
    };

const initialState = {
  isLoading: true,
  data: [],
} as const;

export const MachineContext = createContext<MachineContextType>(initialState);

interface MachineContextProviderProps {
  children: ReactNode;
}

export const MachineContextProvider = (props: MachineContextProviderProps) => {
  const { children } = props;
  const {
    data: rawData,
    isLoading,
    error,
    isValidating,
    mutate,
    swrKey,
  } = useListMachines();
  const [filters, setFilters] = useState<Filters>([]);

  const data = useMemo(() => {
    if (!isLoading && !error && !isValidating && rawData) {
      const { machines } = rawData.data;
      return machines.filter((m) =>
        filters.every((f) => m[f.name] === f.value),
      );
    }
    return [];
  }, [isLoading, error, isValidating, rawData, filters]);

  return (
    <MachineContext.Provider
      value={{
        rawData,
        data,

        isLoading,
        error,
        isValidating,

        filters,
        setFilters,

        swrKey,
        mutate,
      }}
    >
      {children}
    </MachineContext.Provider>
  );
};

export const useMachines = () => React.useContext(MachineContext);
