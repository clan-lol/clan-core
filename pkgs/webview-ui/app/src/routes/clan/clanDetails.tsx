import { OperationResponse, pyApi } from "@/src/api";
import {
  For,
  JSX,
  Match,
  Show,
  Switch,
  createEffect,
  createSignal,
} from "solid-js";
import { SubmitHandler, createForm, required } from "@modular-forms/solid";
import toast from "solid-toast";
import { effect } from "solid-js/web";

interface ClanDetailsProps {
  directory: string;
}

interface ClanFormProps {
  actions: JSX.Element;
}

export const ClanForm = (props: ClanFormProps) => {
  const { actions } = props;
  const [formStore, { Form, Field }] = createForm<ClanMeta>({
    initialValues: {},
  });

  const handleSubmit: SubmitHandler<ClanMeta> = (values, event) => {
    console.log("submit", values);
    pyApi.open_file.dispatch({
      file_request: { mode: "save" },
      op_key: "create_clan",
    });

    pyApi.open_file.receive((r) => {
      if (r.op_key !== "create_clan") {
        return;
      }

      if (r.status !== "success") {
        toast.error("Failed to create clan");
        return;
      }

      if (r.data) {
        pyApi.create_clan.dispatch({
          options: { directory: r.data, meta: values },
        });
      }
    });
  };

  return (
    <div class="card card-compact w-96 bg-base-100 shadow-xl">
      <Form onSubmit={handleSubmit}>
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
          <div class="card-body">
            <Field
              name="name"
              validate={[required("Please enter a unique name for the clan.")]}
            >
              {(field, props) => (
                <label class="form-control w-full max-w-xs">
                  <div class="label">
                    <span class="label-text block after:ml-0.5 after:text-primary after:content-['*']">
                      Name
                    </span>
                  </div>

                  <input
                    {...props}
                    required
                    placeholder="Clan Name"
                    class="input w-full max-w-xs"
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
                <label class="form-control w-full max-w-xs">
                  <div class="label">
                    <span class="label-text">Description</span>
                  </div>

                  <input
                    {...props}
                    required
                    type="text"
                    placeholder="Some words about your clan"
                    class="input w-full max-w-xs"
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
            {actions}
          </div>
        </div>
      </Form>
    </div>
  );
};

// export const EditMetaFields = (props: MetaFieldsProps) => {
//   const { meta, editable, actions, directory } = props;

//   const [editing, setEditing] = createSignal<
//     keyof MetaFieldsProps["meta"] | null
//   >(null);
//   return (

//   );
// };

type ClanMeta = Extract<
  OperationResponse<"show_clan_meta">,
  { status: "success" }
>["data"];

export const ClanDetails = (props: ClanDetailsProps) => {
  const { directory } = props;
  const [loading, setLoading] = createSignal(false);
  const [errors, setErrors] = createSignal<
    | Extract<
        OperationResponse<"show_clan_meta">,
        { status: "error" }
      >["errors"]
    | null
  >(null);
  const [data, setData] = createSignal<ClanMeta>();

  const loadMeta = () => {
    pyApi.show_clan_meta.dispatch({ uri: directory });
    setLoading(true);
  };

  createEffect(() => {
    loadMeta();
    pyApi.show_clan_meta.receive((response) => {
      setLoading(false);
      if (response.status === "error") {
        setErrors(response.errors);
        return console.error(response.errors);
      }
      setData(response.data);
    });
  });
  return (
    <Switch fallback={"loading"}>
      <Match when={loading()}>
        <div>Loading</div>
      </Match>
      <Match when={data()}>
        {(data) => {
          const meta = data();
          return (
            <ClanForm
              meta={meta}
              actions={
                <div class="card-actions justify-between">
                  <button class="btn btn-link" onClick={() => loadMeta()}>
                    Refresh
                  </button>
                  <button class="btn btn-primary">Open</button>
                </div>
              }
            />
          );
        }}
      </Match>
      <Match when={errors()}>
        <button class="btn btn-secondary" onClick={() => loadMeta()}>
          Retry
        </button>
        <For each={errors()}>
          {(item) => (
            <div class="flex flex-col gap-3">
              <span class="bg-red-400 text-white">{item.message}</span>
              <span class="bg-red-400 text-white">{item.description}</span>
              <span class="bg-red-400 text-white">{item.location}</span>
            </div>
          )}
        </For>
      </Match>
    </Switch>
  );
};
