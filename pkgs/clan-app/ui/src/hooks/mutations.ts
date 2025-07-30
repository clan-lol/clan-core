import { useMutation, useQueryClient } from "@tanstack/solid-query";
import { callApi, OperationArgs } from "@/src/hooks/api";
import { encodeBase64 } from "@/src/hooks/clan";

const queryClient = useQueryClient();

export const updateMachine = useMutation(() => ({
  mutationFn: async (args: OperationArgs<"set_machine">) => {
    const call = callApi("set_machine", args);
    return {
      args,
      ...call,
    };
  },
  onSuccess: async ({ args }) => {
    const {
      name,
      flake: { identifier },
    } = args.machine;

    await queryClient.invalidateQueries({
      queryKey: ["clans", encodeBase64(identifier), "machine", name],
    });
  },
}));
