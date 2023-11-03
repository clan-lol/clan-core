import { useListMachines } from "@/api/machine/machine";
import { MachinesResponse } from "@/api/model";
import { AxiosError, AxiosResponse } from "axios";
import React, {
  Dispatch,
  ReactNode,
  SetStateAction,
  createContext,
  useState,
} from "react";
import { KeyedMutator } from "swr";

type AppContextType = {
  //   data: AxiosResponse<{}, any> | undefined;
  data: AppState;

  isLoading: boolean;
  error: AxiosError<any> | undefined;

  setAppState: Dispatch<SetStateAction<AppState>>;
  mutate: KeyedMutator<AxiosResponse<MachinesResponse, any>>;
  swrKey: string | false | Record<any, any>;
};

// const initialState = {
//   isLoading: true,
// } as const;

export const AppContext = createContext<AppContextType>({} as AppContextType);

type AppState = {
  isJoined?: boolean;
  clanName?: string;
};

interface AppContextProviderProps {
  children: ReactNode;
}
export const WithAppState = (props: AppContextProviderProps) => {
  const { children } = props;
  const { isLoading, error, mutate, swrKey } = useListMachines("defaultFlake");

  const [data, setAppState] = useState<AppState>({ isJoined: false });

  return (
    <AppContext.Provider
      value={{
        data,
        setAppState,
        isLoading,
        error,
        swrKey,
        mutate,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useAppState = () => React.useContext(AppContext);
