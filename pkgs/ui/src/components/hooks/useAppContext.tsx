import { AxiosError } from "axios";
import React, {
  Dispatch,
  ReactNode,
  SetStateAction,
  createContext,
  useState,
} from "react";

type AppContextType = {
  //   data: AxiosResponse<{}, any> | undefined;
  data: AppState;

  isLoading: boolean;
  error: AxiosError<any> | undefined;

  setAppState: Dispatch<SetStateAction<AppState>>;
  // mutate: KeyedMutator<AxiosResponse<MachinesResponse, any>>;
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
  const { isLoading, error, swrKey } = {
    isLoading: false,
    error: undefined,
    swrKey: "default",
  };

  const [data, setAppState] = useState<AppState>({ isJoined: false });

  return (
    <AppContext.Provider
      value={{
        data,
        setAppState,
        isLoading,
        error,
        swrKey,
        // mutate,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useAppState = () => React.useContext(AppContext);
