import { Button } from "../../components/Button/Button";
import { registerClan } from "@/src/hooks";
import { useNavigate } from "@solidjs/router";
import { useClanContext } from "@/src/contexts/clan";

export const Welcome = () => {
  const navigate = useNavigate();
  const { setActiveClanURI } = useClanContext();
  return (
    <div class="min-h-[calc(100vh-10rem)]">
      <div class="mb-32 text-center">
        <div class="max-w-md">
          <h1 class="text-5xl font-bold">Welcome to Clan</h1>
          <p class="py-6">Own the services you use.</p>
          <div class="flex flex-col items-start gap-2">
            <Button class="w-full" onClick={() => navigate("/clans/create")}>
              Build your own
            </Button>
            <Button
              variant="light"
              class="w-full text-right !text-primary-800"
              onClick={async () => {
                const uri = await registerClan();
                if (uri) {
                  setActiveClanURI(uri);
                  navigate("/machines");
                }
              }}
            >
              Or select folder
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
