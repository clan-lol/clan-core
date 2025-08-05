import { useStepper } from "@/src/hooks/stepper";
import {
  createForm,
  getError,
  SubmitHandler,
  valiForm,
} from "@modular-forms/solid";
import * as v from "valibot";
import { InstallSteps } from "../install";
import { callApi } from "@/src/hooks/api";
import { Fieldset } from "@/src/components/Form/Fieldset";
import { HostFileInput } from "@/src/components/Form/HostFileInput";
import { Select } from "@/src/components/Select/Select";
import { BackButton, NextButton, StepFooter, StepLayout } from "../../Steps";
import { Typography } from "@/src/components/Typography/Typography";

const CreateHeader = (props: { machineName: string }) => {
  return (
    <div class="px-6 py-2">
      <Typography
        hierarchy="label"
        size="default"
        family="mono"
        weight="medium"
      >
        Create installer
      </Typography>
    </div>
  );
};

const CreateFlashSchema = v.object({
  ssh_key: v.pipe(
    v.string("Please select a key."),
    v.nonEmpty("Please select a key."),
  ),
  language: v.pipe(v.string(), v.nonEmpty("Please choose a language.")),
  keymap: v.pipe(v.string(), v.nonEmpty("Please select a keyboard layout.")),
});

type FlashFormType = v.InferInput<typeof CreateFlashSchema>;

const CreateIso = () => {
  const [formStore, { Form, Field }] = createForm<FlashFormType>({
    validate: valiForm(CreateFlashSchema),
  });
  const stepSignal = useStepper<InstallSteps>();

  // TODO: push values to the parent form Store
  const handleSubmit: SubmitHandler<FlashFormType> = (values, event) => {
    console.log("ISO creation submitted", values);
    // Here you would typically trigger the ISO creation process
    stepSignal.next();
  };

  const onSelectFile = async () => {
    const req = callApi("get_system_file", {
      file_request: {
        mode: "select_folder",
        title: "Select a folder for you new Clan",
      },
    });

    const resp = await req.result;

    if (resp.status === "error") {
      // just throw the first error, I can't imagine why there would be multiple
      // errors for this call
      throw new Error(resp.errors[0].message);
    }

    if (resp.status === "success" && resp.data) {
      return resp.data[0];
    }

    throw new Error("No data returned from api call");
  };

  return (
    <Form onSubmit={handleSubmit}>
      <StepLayout
        body={
          <div class="flex flex-col gap-2">
            <Fieldset>
              <Field name="ssh_key">
                {(field, input) => (
                  <HostFileInput
                    description="Public Key for connecting to the machine"
                    onSelectFile={onSelectFile}
                    {...field}
                    value={field.value}
                    label="Select directory"
                    orientation="horizontal"
                    placeholder="Select SSH Key"
                    required={true}
                    validationState={
                      getError(formStore, "ssh_key") ? "invalid" : "valid"
                    }
                    input={input}
                  />
                )}
              </Field>
            </Fieldset>
            <Fieldset>
              <Field name="language">
                {(field, props) => (
                  <Select
                    {...props}
                    value={field.value}
                    error={field.error}
                    required
                    label={{
                      label: "Language",
                      description: "Select your preferred language",
                    }}
                    options={[
                      { value: "en", label: "English" },
                      { value: "fr", label: "Français" },
                    ]}
                    placeholder="Language"
                    name={field.name}
                  />
                )}
              </Field>
              <Field name="keymap">
                {(field, props) => (
                  <Select
                    {...props}
                    value={field.value}
                    error={field.error}
                    required
                    label={{
                      label: "Keymap",
                      description: "Select your keyboard layout",
                    }}
                    options={[
                      { value: "EN_US", label: "QWERTY" },
                      { value: "DE_DE", label: "QWERTZ" },
                    ]}
                    placeholder="Keymap"
                    name={field.name}
                  />
                )}
              </Field>
            </Fieldset>
          </div>
        }
        footer={
          <div class="flex justify-between">
            <BackButton />
            <NextButton type="submit" />
          </div>
        }
      />
    </Form>
  );
};

export const createInstallerSteps = [
  {
    id: "create:iso-0",
    content: () => (
      <StepLayout
        body={
          <>
            <div class="flex h-36 w-full flex-col justify-center gap-3 rounded-md px-4 py-6 text-fg-inv-1 outline-2 outline-bg-def-acc-3 bg-inv-4">
              <div class="flex flex-col gap-3">
                <Typography
                  hierarchy="label"
                  size="xs"
                  weight="medium"
                  color="inherit"
                >
                  Create a portable installer
                </Typography>
                <Typography
                  hierarchy="headline"
                  size="default"
                  weight="bold"
                  color="inherit"
                >
                  Grab a disposable USB stick and plug it in
                </Typography>
              </div>
            </div>
            <div class="flex flex-col gap-1">
              <Typography hierarchy="body" size="default" weight="bold">
                We will erase everything on it during this process
              </Typography>
              <Typography hierarchy="body" size="xs">
                Create a portable installer tool that can turn any machine into
                a fully configured Clan machine.
              </Typography>
            </div>
          </>
        }
        footer={<StepFooter />}
      />
    ),
  },
  {
    id: "create:iso-1",
    title: CreateHeader,
    content: CreateIso,
  },
] as const;
