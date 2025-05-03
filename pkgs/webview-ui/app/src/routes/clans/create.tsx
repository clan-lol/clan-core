import { callApi, OperationResponse } from "@/src/api";
import { Show } from "solid-js";
import {
  createForm,
  required,
  reset,
  SubmitHandler,
} from "@modular-forms/solid";
import toast from "solid-toast";
import { activeURI, setActiveURI, setClanList } from "@/src/App";
import { TextInput } from "@/src/Form/fields/TextInput";
import { useNavigate } from "@solidjs/router";
import { Button } from "@/src/components/button";
import Icon from "@/src/components/icon";

type CreateForm = Meta & {
  template: string;
};

export const CreateClan = () => {
  const [formStore, { Form, Field }] = createForm<CreateForm>({
    initialValues: {
      name: "",
      description: "",
      template: "minimal",
    },
  });
  const navigate = useNavigate();

  const handleSubmit: SubmitHandler<CreateForm> = async (values, event) => {
    const { template, ...meta } = values;
    const response = await callApi("open_file", {
      file_request: { mode: "save" },
    });

    if (response.status !== "success") {
      toast.error("Cannot select clan directory");
      return;
    }
    const target_dir = response?.data;
    if (!target_dir) {
      toast.error("Cannot select clan directory");
      return;
    }

    const loading_toast = toast.loading("Creating Clan....");
    const r = await callApi("create_clan", {
      opts: {
        dest: target_dir[0],
        template_name: template,
        initial: {
          meta,
          services: {},
          machines: {},
        },
      },
    });
    toast.dismiss(loading_toast);

    if (r.status === "error") {
      toast.error("Failed to create clan");
      return;
    }

    // Will generate a key if it doesn't exist, and add a user to the clan
    const k = await callApi("keygen", {
      flake_dir: target_dir[0],
    });

    if (k.status === "error") {
      toast.error("Failed to generate key");
      return;
    }

    if (r.status === "success") {
      toast.success("Clan Successfully Created");
      setActiveURI(target_dir[0]);
      setClanList((list) => [...list, target_dir[0]]);
      navigate("/machines");
      reset(formStore);
    }
  };

  return (
    <div class="">
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
        <div class="">
          <Field
            name="name"
            validate={[required("Please enter a unique name for the clan.")]}
          >
            {(field, props) => (
              <label class=" w-full">
                <div class="">
                  <span class=" block after:ml-0.5 after:text-primary-800 after:content-['*']">
                    Name
                  </span>
                </div>

                <input
                  {...props}
                  disabled={formStore.submitting}
                  required
                  placeholder="Give your Clan a legendary name"
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
              <label class=" w-full">
                <div class="">
                  <span class="">Description</span>
                </div>

                <input
                  {...props}
                  disabled={formStore.submitting}
                  required
                  type="text"
                  placeholder="Tell us what makes your Clan legendary"
                  classList={{ "": !!field.error }}
                  value={field.value || ""}
                />
                <div class="">
                  {field.error && <span class="">{field.error}</span>}
                </div>
              </label>
            )}
          </Field>
          <Field name="template" validate={[required("This is required")]}>
            {(field, props) => (
              <div class=" " tabindex="0">
                <input type="checkbox" />
                <div class="  font-medium ">Advanced</div>
                <div>
                  <TextInput
                    // adornment={{
                    //   content: (
                    //     <span class="-mr-1 text-neutral-500">clan-core #</span>
                    //   ),
                    //   position: "start",
                    // }}
                    inputProps={props}
                    label="Template to use"
                    value={field.value ?? ""}
                    error={field.error}
                    required
                  />
                </div>
              </div>
            )}
          </Field>
          {
            <div class=" justify-end">
              <Button
                type="submit"
                disabled={formStore.submitting}
                endIcon={<Icon icon="Plus" />}
              >
                Create
              </Button>
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
