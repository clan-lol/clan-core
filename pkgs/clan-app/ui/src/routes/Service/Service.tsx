import { RouteSectionProps, useNavigate } from "@solidjs/router";
import { useClanContext } from "@/src/routes/Clan/Clan";
import { ServiceWorkflow } from "@/src/workflows/Service/Service";
import { SubmitServiceHandler } from "@/src/workflows/Service/models";
import { buildClanPath } from "@/src/hooks/clan";
import { useApiClient } from "@/src/hooks/ApiClient";
import { useQueryClient } from "@tanstack/solid-query";
import { clanKey } from "@/src/hooks/queries";
import { onMount } from "solid-js";

export const Service = (props: RouteSectionProps) => {
  const ctx = useClanContext();

  const navigate = useNavigate();

  const client = useApiClient();

  const queryClient = useQueryClient();

  onMount(() => {
    ctx.setWorldMode("service");
  });

  const handleSubmit: SubmitServiceHandler = async (instance, action) => {
    console.log("Service submitted", instance, action);

    if (action !== "create") {
      console.warn("Updating service instances is not supported yet");
      return;
    }

    const call = client.fetch("create_service_instance", {
      flake: {
        identifier: ctx.clanURI,
      },
      module_ref: instance.module,
      roles: instance.roles,
    });
    const result = await call.result;

    if (result.status === "error") {
      console.error("Error creating service instance", result.errors);
    }

    queryClient.invalidateQueries({
      queryKey: clanKey(ctx.clanURI),
    });

    ctx.setWorldMode("select");
  };

  const handleClose = () => {
    console.log("Service closed, navigating back");
    navigate(buildClanPath(ctx.clanURI), { replace: true });
    ctx.setWorldMode("select");
  };

  return <ServiceWorkflow handleSubmit={handleSubmit} onClose={handleClose} />;
};
