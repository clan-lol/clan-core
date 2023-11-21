import { HTTPValidationError } from "@/api/model";
import { AxiosError } from "axios";
import { useState } from "react";

interface UseVmsOptions {
  url: string;
  attr: string;
}
export const useVms = (options: UseVmsOptions) => {
  const [isLoading] = useState(true);
  const [error] = useState<AxiosError<HTTPValidationError>>();

  return {
    error,
    isLoading,
  };
};
