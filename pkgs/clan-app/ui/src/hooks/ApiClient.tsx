import { createContext, JSX, useContext } from "solid-js";
import { ApiCall, OperationArgs, OperationNames } from "./api";

export interface ApiClient {
  fetch: Fetcher;
}

export type Fetcher = <K extends OperationNames>(
  method: K,
  args: OperationArgs<K>,
) => ApiCall<K>;

const ApiClientContext = createContext<ApiClient>();

interface ApiClientProviderProps {
  client: ApiClient;
  children: JSX.Element;
}
export const ApiClientProvider = (props: ApiClientProviderProps) => {
  return (
    <ApiClientContext.Provider value={props.client}>
      {props.children}
    </ApiClientContext.Provider>
  );
};

export const useApiClient = () => {
  const client = useContext(ApiClientContext);
  if (!client) {
    throw new Error("useApiClient must be used within an ApiClientProvider");
  }
  return client;
};
