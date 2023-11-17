import { HTTPValidationError } from "@/api/model";
import { AxiosError } from "axios";
import { toast } from "react-hot-toast";

export function clanErrorToast(error: AxiosError<HTTPValidationError>) {
  console.error({ error });
  const detail = error.response?.data.detail?.[0]?.msg;
  const cause = error.cause?.message;
  const axiosMessage = error.message;
  const sanitizedMsg = detail || cause || axiosMessage || "Unexpected error";
  toast.error(sanitizedMsg);
}
