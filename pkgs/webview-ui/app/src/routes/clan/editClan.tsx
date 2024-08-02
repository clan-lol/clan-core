import { callApi, OperationResponse, pyApi } from "@/src/api";
import { Accessor, Match, Show, Switch } from "solid-js";
import {
  createForm,
  required,
  reset,
  SubmitHandler,
} from "@modular-forms/solid";
import toast from "solid-toast";
import { createQuery } from "@tanstack/solid-query";

type CreateForm = Meta;

interface EditClanFormProps {
  directory: Accessor<string>;
  done: () => void;
}
export const EditClanForm = (props: EditClanFormProps) => {
  const { directory } = props;
  const details = createQuery(() => ({
    queryKey: [directory(), "meta"],
    queryFn: async () => {
      const result = await callApi("show_clan_meta", { uri: directory() });
      if (result.status === "error") throw new Error("Failed to fetch data");
      return result.data;
    },
  }));

  return (
    <Switch>
      <Match when={details?.data}>
        {(data) => (
          <FinalEditClanForm
            initial={data()}
            directory={directory()}
            done={props.done}
          />
        )}
      </Match>
    </Switch>
  );
};

interface FinalEditClanFormProps {
  initial: CreateForm;
  directory: string;
  done: () => void;
}
export const FinalEditClanForm = (props: FinalEditClanFormProps) => {
  const [formStore, { Form, Field }] = createForm<CreateForm>({
    initialValues: props.initial,
  });

  const handleSubmit: SubmitHandler<CreateForm> = async (values, event) => {
    await toast.promise(
      (async () => {
        await callApi("update_clan_meta", {
          options: {
            directory: props.directory,
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
    props.done();
  };

  return (
    <div class="card card-normal">
      <Form onSubmit={handleSubmit} shouldActive>
        <Field name="icon">
          {(field, props) => (
            <>
              <figure>
                <Show
                  when={field.value}
                  fallback={
                    <span class="material-icons aspect-square size-60 rounded-lg text-[18rem]">
                      group
                    </span>
                  }
                >
                  {(icon) => (
                    <img
                      class="aspect-square size-60 rounded-lg"
                      src={icon()}
                      alt="Clan Logo"
                    />
                  )}
                </Show>
              </figure>
            </>
          )}
        </Field>
        <div class="card-body">
          <Field
            name="name"
            validate={[required("Please enter a unique name for the clan.")]}
          >
            {(field, props) => (
              <label class="form-control w-full">
                <div class="label">
                  <span class="label-text block after:ml-0.5 after:text-primary after:content-['*']">
                    Name
                  </span>
                </div>

                <input
                  {...props}
                  disabled={formStore.submitting}
                  required
                  placeholder="Clan Name"
                  class="input input-bordered"
                  classList={{ "input-error": !!field.error }}
                  value={field.value}
                />
                <div class="label">
                  {field.error && (
                    <span class="label-text-alt">{field.error}</span>
                  )}
                </div>
              </label>
            )}
          </Field>
          <Field name="description">
            {(field, props) => (
              <label class="form-control w-full">
                <div class="label">
                  <span class="label-text">Description</span>
                </div>

                <input
                  {...props}
                  disabled={formStore.submitting}
                  required
                  type="text"
                  placeholder="Some words about your clan"
                  class="input input-bordered"
                  classList={{ "input-error": !!field.error }}
                  value={field.value || ""}
                />
                <div class="label">
                  {field.error && (
                    <span class="label-text-alt">{field.error}</span>
                  )}
                </div>
              </label>
            )}
          </Field>
          {
            <div class="card-actions justify-end">
              <button
                class="btn btn-primary"
                type="submit"
                disabled={formStore.submitting}
              >
                Save
              </button>
            </div>
          }
        </div>
      </Form>
    </div>
  );
};

type Meta = Extract<
  OperationResponse<"show_clan_meta">,
  { status: "success" }
>["data"];
