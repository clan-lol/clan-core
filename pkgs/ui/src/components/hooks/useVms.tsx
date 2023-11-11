import { HTTPValidationError, VmConfig } from "@/api/model";
import { inspectVm } from "@/api/vm/vm";
import { AxiosError } from "axios";
import { useEffect, useState } from "react";
import { toast } from "react-hot-toast";

interface UseVmsOptions {
  url: string;
  attr: string;
}
export const useVms = (options: UseVmsOptions) => {
  const { url, attr } = options;
  const [isLoading, setIsLoading] = useState(true);
  const [config, setConfig] = useState<VmConfig>();
  const [error, setError] = useState<AxiosError<HTTPValidationError>>();

  useEffect(() => {
    const getVmInfo = async (url: string, attr: string) => {
      if (url === "" || !url) {
        toast.error("Flake url is missing", { id: "missing.flake.url" });
        return undefined;
      }
      try {
        const response = await inspectVm({
          flake_attr: attr,
          flake_url: url,
        });
        const {
          data: { config },
        } = response;
        setError(undefined);
        return config;
      } catch (e) {
        const err = e as AxiosError<HTTPValidationError>;
        setError(err);
        toast(
          "Could not find default configuration. Please select a machine preset",
        );
        return undefined;
      } finally {
        setIsLoading(false);
      }
    };
    getVmInfo(url, attr).then((c) => setConfig(c));
  }, [url, attr]);

  return {
    error,
    isLoading,
    config,
  };
};
