import {
  Accessor,
  createSignal,
  JSX,
  Match,
  Setter,
  Show,
  Switch,
} from "solid-js";
import styles from "./Onboarding.module.css";
import { Typography } from "@/src/components/Typography/Typography";
import { Button } from "@/src/components/Button/Button";
import { Alert } from "@/src/components/Alert/Alert";

import { Divider } from "@/src/components/Divider/Divider";
import { Logo } from "@/src/components/Logo/Logo";
import {
  createForm,
  getError,
  getErrors,
  SubmitHandler,
  valiForm,
} from "@modular-forms/solid";
import { TextInput } from "@/src/components/Form/TextInput";
import { TextArea } from "@/src/components/Form/TextArea";
import { Fieldset } from "@/src/components/Form/Fieldset";
import * as v from "valibot";
import { HostFileInput } from "@/src/components/Form/HostFileInput";
import ListClansModal from "@/src/components/Modal/ListClansModal";
import { Tooltip } from "@/src/components/Tooltip/Tooltip";
import { CubeConstruction } from "@/src/components/CubeConstruction/CubeConstruction";
import { useClansContext } from "@/src/models";

type Step = {
  type: "welcome" | "setup" | "creating";
  error?: string;
};

const SetupSchema = v.object({
  name: v.pipe(
    v.string(),
    v.nonEmpty("Please enter a name."),
    v.regex(
      new RegExp("^[a-zA-Z0-9_\\-]+$"),
      "Name must be alphanumeric and can contain underscores and dashes, without spaces.",
    ),
  ),
  description: v.pipe(v.string(), v.nonEmpty("Please describe your clan.")),
  directory: v.pipe(v.string(), v.nonEmpty("Please select a directory.")),
});

type SetupForm = v.InferInput<typeof SetupSchema>;

export default function Onboarding(): JSX.Element {
  const [, { createClan }] = useClansContext();
  const [step, setStep] = createSignal<Step>({ type: "welcome" });

  //
  const [setupForm, { Form, Field }] = createForm<SetupForm>({
    validate: valiForm(SetupSchema),
  });

  const formError = () => {
    const formErrors = getErrors(setupForm);
    return formErrors.name || formErrors.description || formErrors.directory;
  };

  const onSubmit: SubmitHandler<SetupForm> = async (
    { name, description, directory },
    event,
  ) => {
    const path = `${directory}/${name}`;
    const data = { name, description };
    setStep({ type: "creating" });
    try {
      await createClan(path, data);
    } catch (err) {
      setStep({ type: "welcome", error: String(err) });
      return;
    }
  };

  return (
    <main class={styles.onboarding}>
      <Background />
      <div class={styles.container}>
        <Switch>
          <Match when={step().type === "welcome"}>
            <Welcome step={step} setStep={setStep} />
          </Match>
          <Match when={step().type === "setup"}>
            <div class={styles.setup}>
              <div class={styles.setupHeader}>
                <Button
                  hierarchy="secondary"
                  ghost={true}
                  icon="ArrowLeft"
                  onClick={() => setStep({ type: "welcome" })}
                />
                <Typography hierarchy="headline" size="default" weight="bold">
                  Setup
                </Typography>
              </div>
              <Form onSubmit={onSubmit}>
                {formError() && (
                  <Alert
                    type="error"
                    icon="Info"
                    title="Form error"
                    description={formError()}
                  />
                )}
                <Fieldset name="meta">
                  <Field name="name">
                    {(field, input) => (
                      <TextInput
                        label="Name"
                        required
                        orientation="horizontal"
                        validationState={
                          getError(setupForm, "name") ? "invalid" : "valid"
                        }
                        input={{
                          ...input,
                          placeholder: "Name your Clan",
                        }}
                      />
                    )}
                  </Field>
                  <Divider />
                  <Field name="description">
                    {(field, input) => (
                      <TextArea
                        label="Description"
                        required
                        orientation="horizontal"
                        validationState={
                          getError(setupForm, "description")
                            ? "invalid"
                            : "valid"
                        }
                        input={input}
                      />
                    )}
                  </Field>
                </Fieldset>

                <Fieldset name="location">
                  <Field name="directory">
                    {(field, props) => (
                      <HostFileInput
                        {...props}
                        windowTitle="Select a folder for you new Clan"
                        label="Select directory"
                        orientation="horizontal"
                        required={true}
                      />
                    )}
                  </Field>
                </Fieldset>

                <div class={styles.setupFormControls}>
                  <Button
                    type="submit"
                    hierarchy="primary"
                    endIcon="ArrowRight"
                  >
                    Next
                  </Button>
                </div>
              </Form>
            </div>
          </Match>

          <Match when={step().type === "creating"}>
            <div class={styles.creating}>
              <Tooltip
                open={true}
                placement="top"
                description={"Your Clan is being created"}
              >
                <div></div>
              </Tooltip>
              <CubeConstruction />
            </div>
          </Match>
        </Switch>
      </div>
    </main>
  );
}

function Background(): JSX.Element {
  // controls whether the list clans modal is displayed
  const [showModal, setShowModal] = createSignal(false);

  return (
    <div class={styles.background}>
      <div class={styles.backgroundLayer1} />
      <div class={styles.backgroundLayer2} />
      <div class={styles.backgroundLayer3} />
      <Logo variant="Clan" inverted />
      <div class={styles.listClans}>
        <Button
          hierarchy="primary"
          ghost
          size="s"
          icon="Grid"
          onClick={() => setShowModal(true)}
        >
          All Clans
        </Button>
      </div>
      <Show when={showModal()}>
        <ListClansModal onClose={() => setShowModal(false)} />
      </Show>
    </div>
  );
}

function Welcome(props: {
  step: Accessor<Step>;
  setStep: Setter<Step>;
}): JSX.Element {
  const [, { pickClanDir, loadClan }] = useClansContext()!;
  const [loading, setLoading] = createSignal(false);

  async function onSelect(): Promise<void> {
    setLoading(true);
    // TODO display error, currently we don't get anything to distinguish between cancel or an actual error
    let path;
    try {
      path = await pickClanDir();
    } catch (err) {
      setLoading(false);
      return;
    }
    setLoading(false);
    await loadClan(path);
  }

  return (
    <div class={styles.welcome}>
      <Typography
        hierarchy="headline"
        size="xxl"
        weight="bold"
        align="center"
        inverted={true}
      >
        Build your own
        <br />
        Clan
      </Typography>
      {props.step().error && (
        <Alert
          type="error"
          icon="Info"
          title="Your Clan creation failed"
          description={props.step().error || ""}
        />
      )}
      <Button
        hierarchy="secondary"
        onClick={() => {
          props.setStep({ type: "setup" });
        }}
      >
        Start building
      </Button>
      <div class={styles.welcomeSeparator}>
        <Divider orientation="horizontal" />
        <Typography
          hierarchy="body"
          size="s"
          weight="medium"
          inverted={true}
          align="center"
        >
          or
        </Typography>
        <Divider orientation="horizontal" />
      </div>
      <Button hierarchy="primary" ghost loading={loading()} onClick={onSelect}>
        Select existing Clan
      </Button>
    </div>
  );
}
