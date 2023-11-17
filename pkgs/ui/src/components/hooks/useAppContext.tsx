// import { useListAllFlakes } from "@/api/flake/flake";
// import { FlakeListResponse } from "@/api/model";
import { AxiosError } from "axios";
import React, {
  Dispatch,
  ReactNode,
  SetStateAction,
  createContext,
  useEffect,
  useState,
} from "react";

type AppContextType = {
  //   data: AxiosResponse<{}, any> | undefined;
  data: AppState;

  isLoading: boolean;
  error: AxiosError<any> | undefined;

  setAppState: Dispatch<SetStateAction<AppState>>;
  // mutate: KeyedMutator<AxiosResponse<FlakeListResponse, any>>;
  swrKey: string | false | Record<any, any>;
};

export const AppContext = createContext<AppContextType>({} as AppContextType);

type AppState = {
  isJoined?: boolean;
  clanDir?: string;
  flakes?: string[]; //FlakeListResponse["flakes"];
};

interface AppContextProviderProps {
  children: ReactNode;
}
const mock = {
  data: { flakes: [] },
};

// list_clans

export const WithAppState = (props: AppContextProviderProps) => {
  const { children } = props;
  // const {
  //   isLoading,
  //   error,
  //   swrKey,
  //   data: flakesResponse,
  //   mutate,
  // } = useListAllFlakes({
  //   swr: {
  //     revalidateIfStale: false,
  //     revalidateOnFocus: false,
  //     revalidateOnReconnect: false,
  //   },
  // });
  const {
    isLoading,
    error,
    swrKey,
    data: flakesResponse,
  } = {
    isLoading: false,
    error: undefined,
    swrKey: "",
    data: mock,
  };
  const [data, setAppState] = useState<AppState>({ isJoined: false });

  useEffect(() => {
    if (!isLoading && !error && flakesResponse) {
      const {
        data: { flakes },
      } = flakesResponse;
      if (flakes.length >= 1) {
        setAppState((c) => ({ ...c, clanDir: flakes[0], isJoined: true }));
      }
      setAppState((c) => ({ ...c, flakes }));
    }
  }, [flakesResponse, error, isLoading]);

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
