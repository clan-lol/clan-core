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
import {
  SubmitHandler,
  createForm,
  email,
  required,
} from "@modular-forms/solid";

interface ClanDetailsProps {
  directory: string;
}

interface MetaFieldsProps {
  meta: ClanMeta;
  actions: JSX.Element;
  editable?: boolean;
  directory?: string;
}

const fn = (e: SubmitEvent) => {
  e.preventDefault();
  console.log("form submit", e.currentTarget);
};

export default function Login() {
  const [, { Form, Field }] = createForm<ClanMeta>({
    initialValues: { name: "MyClan" },
  });

  const handleSubmit: SubmitHandler<ClanMeta> = (values, event) => {
    pyApi.open_file.dispatch({ file_request: { mode: "save" } });
    pyApi.open_file.receive((r) => {
      if (r.status === "success") {
        if (r.data) {
          pyApi.create_clan.dispatch({
            options: { directory: r.data, meta: values },
          });
        }

        return;
      }
    });
    console.log("submit", values);
  };
  return (
    <div class="card-body">
      <Form onSubmit={handleSubmit}>
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
                type="email"
                required
                placeholder="your.mail@example.com"
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
        <Field name="icon">
          {(field, props) => (
            <label class="form-control w-full max-w-xs">
              <div class="label">
                <span class="label-text">Select icon</span>
              </div>
              <input
                type="file"
                class="file-input file-input-bordered w-full max-w-xs"
              />
              <div class="label">
                {field.error && (
                  <span class="label-text-alt">{field.error}</span>
                )}
              </div>
            </label>
          )}
        </Field>
        <div class="card-actions justify-end">
          <button class="btn btn-primary" type="submit">
            Create
          </button>
        </div>
      </Form>
    </div>
  );
}

export const EditMetaFields = (props: MetaFieldsProps) => {
  const { meta, editable, actions, directory } = props;

  const [editing, setEditing] = createSignal<
    keyof MetaFieldsProps["meta"] | null
  >(null);
  return (
    <div class="card card-compact w-96 bg-base-100 shadow-xl">
      <figure>
        <img
          src="https://www.shutterstock.com/image-vector/modern-professional-ninja-mascot-logo-260nw-1729854862.jpg"
          alt="Clan Logo"
        />
      </figure>
      <div class="card-body">
        <Login />
        {/* <form onSubmit={fn}> */}
        {/* <h2 class="card-title justify-between">
            <input
              classList={{
                [cx("text-slate-600")]: editing() !== "name",
              }}
              readOnly={editing() !== "name"}
              class="w-full"
              autofocus
              onBlur={() => setEditing(null)}
              type="text"
              value={meta?.name}
              onInput={(e) => {
                console.log(e.currentTarget.value);
              }}
            />
            <Show when={editable}>
              <button class="btn btn-square btn-ghost btn-sm">
                <span
                  class="material-icons"
                  onClick={() => {
                    if (editing() !== "name") setEditing("name");
                    else {
                      setEditing(null);
                    }
                  }}
                >
                  <Show when={editing() !== "name"} fallback="check">
                    edit
                  </Show>
                </span>
              </button>
            </Show>
          </h2>
          <div class="flex gap-1 align-middle leading-8">
            <i class="material-icons">description</i>
            <span>{meta?.description || "No description"}</span>
          </div>
          <Show when={directory}>
            <div class="flex gap-1 align-middle leading-8">
              <i class="material-icons">folder</i>
              <span>{directory}</span>
            </div>
          </Show>
          {actions} */}
        {/* </form> */}
      </div>
    </div>
  );
};

type ClanMeta = Extract<
  OperationResponse<"show_clan_meta">,
  { status: "success" }
>["data"];

export const ClanDetails = (props: ClanDetailsProps) => {
  const { directory } = props;
  const [, setLoading] = createSignal(false);
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
      <Match when={data()}>
        <EditMetaFields
          directory={directory}
          // @ts-expect-error: TODO: figure out how solid allows type narrowing this
          meta={data()}
          actions={
            <div class="card-actions justify-between">
              <button class="btn btn-link" onClick={() => loadMeta()}>
                Refresh
              </button>
              <button class="btn btn-primary">Open</button>
            </div>
          }
        />
      </Match>
      <Match when={errors()}>
        <button class="btn btn-link" onClick={() => loadMeta()}>
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
