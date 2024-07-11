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
  required,
  custom,
} from "@modular-forms/solid";
import toast from "solid-toast";
import { setActiveURI, setRoute } from "@/src/App";

interface ClanDetailsProps {
  directory: string;
}

type CreateForm = Meta & {
  template_url: string;
};

export const ClanForm = () => {
  const [formStore, { Form, Field }] = createForm<CreateForm>({
    initialValues: {
      template_url: "git+https://git.clan.lol/clan/clan-core#templates.minimal",
    },
  });

  const handleSubmit: SubmitHandler<CreateForm> = async (values, event) => {
    const { template_url, ...meta } = values;
    pyApi.open_file.dispatch({
      file_request: {
        mode: "save",
      },

      op_key: "create_clan",
    });

    // await new Promise<void>((done) => {
    //   pyApi.open_file.receive((r) => {
    //     if (r.op_key !== "create_clan") {
    //       done();
    //       return;
    //     }
    //     if (r.status !== "success") {
    //       toast.error("Cannot select clan directory");
    //       done();
    //       return;
    //     }
    //     const target_dir = r?.data;
    //     if (!target_dir) {
    //       toast.error("Cannot select clan directory");
    //       done();
    //       return;
    //     }

    //     console.log({ formStore });

    //     toast.promise(
    //       new Promise<void>((resolve, reject) => {
    //         pyApi.create_clan.receive((r) => {
    //           done();
    //           if (r.status === "error") {
    //             reject();
    //             console.error(r.errors);
    //             return;
    //           }
    //           resolve();

    //           // Navigate to the new clan
    //           setCurrClanURI(target_dir);
    //           setRoute("machines");
    //         });

    //         pyApi.create_clan.dispatch({
    //           options: { directory: target_dir, meta, template_url },
    //           op_key: "create_clan",
    //         });
    //       }),
    //       {
    //         loading: "Creating clan...",
    //         success: "Clan Successfully Created",
    //         error: "Failed to create clan",
    //       }
    //     );
    //   });
    // });
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
          <Field name="template_url" validate={[required("This is required")]}>
            {(field, props) => (
              <div class="collapse collapse-arrow" tabindex="0">
                <input type="checkbox" />
                <div class="collapse-title link font-medium ">Advanced</div>
                <div class="collapse-content">
                  <label class="form-control w-full">
                    <div class="label ">
                      <span class="label-text  after:ml-0.5 after:text-primary after:content-['*']">
                        Template to use
                      </span>
                    </div>
                    <input
                      {...props}
                      required
                      type="text"
                      placeholder="Template to use"
                      class="input input-bordered"
                      classList={{ "input-error": !!field.error }}
                      value={field.value}
                    />
                  </label>
                </div>
              </div>
            )}
          </Field>
          {
            <div class="card-actions justify-end">
              <button
                class="btn btn-primary"
                type="submit"
                disabled={formStore.submitting}
              >
                Create
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
