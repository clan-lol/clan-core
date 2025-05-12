import { callApi, ClanServiceInstance, SuccessQuery } from "@/src/api";
import { useParams } from "@solidjs/router";
import { createQuery, useQueryClient } from "@tanstack/solid-query";
import { createSignal, For, Match, Switch } from "solid-js";
import {
  createForm,
  FieldValues,
  getValue,
  getValues,
  required,
  setValue,
  SubmitHandler,
} from "@modular-forms/solid";
import { TextInput } from "@/src/Form/fields/TextInput";
import toast from "solid-toast";
import { set_single_service } from "@/src/api/inventory";
import { Button } from "@/src/components/button";
import Icon from "@/src/components/icon";
import { Header } from "@/src/layout/header";

interface EditClanFormProps {
  initial: GeneralData;
  directory: string;
}

const EditClanForm = (props: EditClanFormProps) => {
  const [formStore, { Form, Field }] = createForm<GeneralData>({
    initialValues: props.initial,
  });
  const queryClient = useQueryClient();

  const handleSubmit: SubmitHandler<GeneralData> = async (values, event) => {
    await toast.promise(
      (async () => {
        await callApi("update_clan_meta", {
          options: {
            flake: { identifier: props.directory },
            meta: values,
          },
        });
      })(),
      {
        loading: "Updating clan...",
        success: "Clan Successfully updated",
        error: "Failed to update clan",
      },
    );
    queryClient.invalidateQueries({
      queryKey: [props.directory, "meta"],
    });
  };
  const curr_name = () => props.initial.name;

  return (
    <Form onSubmit={handleSubmit} shouldActive>
      <Field name="icon">
        {(field) => (
          <>
            <div class="flex flex-col items-center">
              <div class="text-3xl text-primary-800">{curr_name()}</div>
              <div class="text-secondary-800">Wide settings</div>
              <Icon
                class="mt-4"
                icon="ClanIcon"
                viewBox="0 0 72 89"
                width={96}
                height={96}
              />
            </div>
          </>
        )}
      </Field>
      <div class="">
        <span class="text-xl text-primary-800">General</span>
        <Field
          name="name"
          validate={[required("Please enter a unique name for the clan.")]}
        >
          {(field, props) => (
            <label class="w-full">
              <div class="">
                <span class=" block after:ml-0.5 after:text-primary-800 after:content-['*']">
                  Name
                </span>
              </div>

              <input
                {...props}
                disabled={formStore.submitting}
                required
                placeholder="Clan Name"
                class=""
                classList={{ "": !!field.error }}
                value={field.value}
              />
              <div class="">
                {field.error && <span class="">{field.error}</span>}
              </div>
            </label>
          )}
        </Field>
        <Field name="description">
          {(field, props) => (
            <label class="w-full">
              <div class="">
                <span class="">Description</span>
              </div>

              <input
                {...props}
                disabled={formStore.submitting}
                required
                type="text"
                placeholder="Some words about your clan"
                class=""
                classList={{ "": !!field.error }}
                value={field.value || ""}
              />
              <div class="">
                {field.error && <span class="">{field.error}</span>}
              </div>
            </label>
          )}
        </Field>
        {
          <div class="justify-end">
            <Button
              type="submit"
              disabled={formStore.submitting || !formStore.dirty}
            >
              Save
            </Button>
          </div>
        }
      </div>
    </Form>
  );
};

type GeneralData = SuccessQuery<"show_clan_meta">["data"];

export const ClanDetails = () => {
  const params = useParams();
  const clan_dir = window.atob(params.id);
  // Fetch general meta data
  const clanQuery = createQuery(() => ({
    queryKey: [clan_dir, "inventory", "meta"],
    queryFn: async () => {
      const result = await callApi("show_clan_meta", {
        flake: { identifier: clan_dir },
      });
      if (result.status === "error") throw new Error("Failed to fetch data");
      return result.data;
    },
  }));

  return (
    <>
      <Header title={clan_dir} showBack />
      <div class="flex flex-col justify-center">
        <Switch fallback={<>General data not available</>}>
          <Match when={clanQuery.data}>
            {(d) => <EditClanForm initial={d()} directory={clan_dir} />}
          </Match>
        </Switch>
      </div>
    </>
  );
};
