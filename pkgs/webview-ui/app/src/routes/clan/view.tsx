import { pyApi } from "@/src/api";
import { Match, Switch, createEffect, createSignal } from "solid-js";
import toast from "solid-toast";
import { ClanDetails, ClanForm } from "./clanDetails";

export const CreateClan = () => {
  // const [mode, setMode] = createSignal<"init" | "open" | "create">("init");
  const [clanDir, setClanDir] = createSignal<string | null>(null);

  // createEffect(() => {
  //   console.log(mode());
  // });
  return (
    <div>
      <ClanForm
        actions={
          <div class="card-actions justify-end">
            <button class="btn btn-primary" type="submit">
              Create
            </button>
          </div>
        }
      />
    </div>
  );
};
