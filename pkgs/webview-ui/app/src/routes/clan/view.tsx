import { pyApi } from "@/src/api";
import { Match, Switch, createEffect, createSignal } from "solid-js";
import toast from "solid-toast";
import { ClanDetails, ClanForm } from "./clanDetails";

export const CreateClan = () => {
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
