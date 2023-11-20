import { HTTPValidationError } from "@/api/model";
import { AxiosError } from "axios";
import { toast } from "react-hot-toast";

export function clanErrorToast(error: AxiosError<HTTPValidationError>) {
  console.error({ error });
  const detail = error.response?.data.detail?.[0]?.msg;
  const detailAlt = error.response?.data.detail as unknown as string;
  const cause = error.cause?.message;
  const axiosMessage = error.message;
  const sanitizedMsg =
    detail || detailAlt || cause || axiosMessage || "Unexpected error";
  toast.error(sanitizedMsg);
}
