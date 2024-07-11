import { callApi } from "@/src/api";
import {
  SubmitHandler,
  createForm,
  required,
  setValue,
} from "@modular-forms/solid";
import { activeURI, setClanList, setActiveURI, setRoute } from "@/src/App";

// eslint-disable-next-line @typescript-eslint/consistent-type-definitions
type SettingsForm = {
  base_dir: string | null;
};

export const registerClan = async () => {
  try {
    const loc = await callApi("open_file", {
      file_request: { mode: "select_folder" },
    });
    console.log(loc);
    if (loc.status === "success" && loc.data) {
      // @ts-expect-error: data is a string
      setClanList((s) => [...s, loc.data]);
      setRoute((r) => {
        if (r === "welcome") return "machines";
        return r;
      });
      return loc.data;
    }
  } catch (e) {
    //
  }
};

export const Settings = () => {
  const [formStore, { Form, Field }] = createForm<SettingsForm>({
    initialValues: {
      base_dir: activeURI(),
    },
  });

  const handleSubmit: SubmitHandler<SettingsForm> = async (values, event) => {
    //
  };

  return (
    <div class="card card-normal">
      <Form onSubmit={handleSubmit} shouldActive>
        <div class="card-body">
          <Field name="base_dir" validate={[required("Clan URI is required")]}>
            {(field, props) => (
              <label class="form-control w-full">
                <div class="label">
                  <span class="label-text block after:ml-0.5 after:text-primary">
                    Directory
                  </span>
                </div>
                <div class="stats shadow">
                  <div class="stat">
                    <div class="stat-figure text-primary">
                      <span class="material-icons">inventory</span>
                    </div>
                    <div class="stat-title">Clan URI</div>
                    <div
                      class="stat-value"
                      classList={{ "text-slate-500": !field.value }}
                    >
                      {field.value || "Not set"}
                      <button
                        class="btn btn-ghost mx-4"
                        onClick={async () => {
                          const location = await registerClan();
                          if (location) {
                            setActiveURI(location);
                            setValue(formStore, "base_dir", location);
                          }
                        }}
                      >
                        <span class="material-icons">edit</span>
                      </button>
                    </div>
                    <div class="stat-desc">Where the clan source resides</div>
                  </div>
                </div>

                <div class="label">
                  {field.error && (
                    <span class="label-text-alt">{field.error}</span>
                  )}
                </div>
              </label>
            )}
          </Field>
        </div>
      </Form>
    </div>
  );
};
