"use client";

import { useListMachines } from "@/api/machine/machine";
import { Machine, MachinesResponse } from "@/api/model";
import { clanErrorToast } from "@/error/errorToast";
import { AxiosError, AxiosResponse } from "axios";
import React, {
  Dispatch,
  ReactNode,
  SetStateAction,
  createContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { KeyedMutator } from "swr";

type PartialRecord<K extends keyof any, T> = {
  [P in K]?: T;
};

export type MachineFilter = PartialRecord<
  keyof Machine,
  Machine[keyof Machine]
>;

type MachineContextType = {
  rawData: AxiosResponse<MachinesResponse, any> | undefined;
  data: Machine[];
  isLoading: boolean;
  error: AxiosError<any> | undefined;
  isValidating: boolean;

  filters: MachineFilter;
  setFilters: Dispatch<SetStateAction<MachineFilter>>;
  mutate: KeyedMutator<AxiosResponse<MachinesResponse, any>>;
  swrKey: string | false | Record<any, any>;
};

export function CreateMachineContext() {
  return createContext<MachineContextType>({} as MachineContextType);
}

interface MachineContextProviderProps {
  children: ReactNode;
  clanDir: string;
}

const MachineContext = CreateMachineContext();

export const MachineContextProvider = (props: MachineContextProviderProps) => {
  const { children, clanDir } = props;
  const {
    data: rawData,
    isLoading,
    error,
    isValidating,
    mutate,
    swrKey,
  } = useListMachines({ flake_dir: clanDir });

  const [filters, setFilters] = useState<MachineFilter>({});

  useEffect(() => {
    if (error) {
      clanErrorToast(error);
    }
  }, [error]);

  const data = useMemo(() => {
    if (!isLoading && rawData) {
      const { machines } = rawData.data;
      return machines.filter(
        (m) =>
          !filters.name ||
          m.name.toLowerCase().includes(filters.name.toLowerCase()),
      );
    }
    return [];
  }, [isLoading, filters, rawData]);

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
