"use client";

import { useListMachines } from "@/api/default/default";
import { Machine, MachinesResponse } from "@/api/model";
import { AxiosError, AxiosResponse } from "axios";
import React, {
  Dispatch,
  ReactNode,
  SetStateAction,
  createContext,
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
      flakeName: string;
      error: AxiosError<any> | undefined;
      isValidating: boolean;

      filters: Filters;
      setFilters: Dispatch<SetStateAction<Filters>>;
      mutate: KeyedMutator<AxiosResponse<MachinesResponse, any>>;
      swrKey: string | false | Record<any, any>;
    }
  | {
      flakeName: string;
      isLoading: true;
      data: readonly [];
    };

const initialState = {
  isLoading: true,
  data: [],
} as const;


export function CreateMachineContext(flakeName: string) {
  return useMemo(() => {
    return createContext<MachineContextType>({
      ...initialState,
      flakeName,
    });
  }, [flakeName]);
}

interface MachineContextProviderProps {
  children: ReactNode;
  flakeName: string;
}

export const MachineContextProvider = (props: MachineContextProviderProps) => {
  const { children, flakeName } = props;
  const {
    data: rawData,
    isLoading,
    error,
    isValidating,
    mutate,
    swrKey,
  } = useListMachines(flakeName);
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

  const MachineContext = CreateMachineContext(flakeName);

  return (
    <MachineContext.Provider
      value={{
        rawData,
        data,

        isLoading,
        flakeName,
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

export const useMachines = (flakeName: string) => React.useContext(CreateMachineContext(flakeName));
