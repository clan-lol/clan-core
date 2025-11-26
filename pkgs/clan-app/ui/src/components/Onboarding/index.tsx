import {
  Accessor,
  Component,
  createSignal,
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
  FormStore,
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
import { ListClansModal } from "@/src/modals/ListClansModal/ListClansModal";
import { Tooltip } from "@/src/components/Tooltip/Tooltip";
import { CubeConstruction } from "@/src/components/CubeConstruction/CubeConstruction";
import * as api from "@/src/api";
import { useClanContext } from "@/src/contexts/ClanContext";

type State = "welcome" | "setup" | "creating";

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

const background = (props: { state: State; form: FormStore<SetupForm> }) => {
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
};

const welcome = (props: {
  setState: Setter<State>;
  welcomeError: Accessor<string | undefined>;
  setWelcomeError: Setter<string | undefined>;
}) => {
  const { clans } = useClanContext()!;
  const [loading, setLoading] = createSignal(false);

  const onSelect = async () => {
    setLoading(true);
    // TODO display error, currently we don't get anything to distinguish between cancel or an actual error
    let path;
    try {
      path = await api.clan.getClanDir();
    } catch (err) {
      setLoading(false);
      return;
    }
    setLoading(false);
    clans()?.add({ id: path });
  };

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
      {props.welcomeError() && (
        <Alert
          type="error"
          icon="Info"
          title="Your Clan creation failed"
          description={props.welcomeError() || ""}
        />
      )}
      <Button
        hierarchy="secondary"
        onClick={() => {
          // reset welcome error
          props.setWelcomeError(undefined);
          // move to next step
          props.setState("setup");
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
};

export const Onboarding: Component = () => {
  const { clans } = useClanContext()!;
  const [state, setState] = createSignal<State>("welcome");

  // used to display an error in the welcome screen in the event of a failed
  // clan creation
  const [welcomeError, setWelcomeError] = createSignal<string | undefined>();

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
    setState("creating");
    try {
      await clans()?.create(path, data);
    } catch (err) {
      setWelcomeError(String(err));
      setState("welcome");
      return;
    }
  };

  return (
    <main class={styles.onboarding}>
      {background({ form: setupForm, state: state() })}
      <div class={styles.container}>
        <Switch>
          <Match when={state() === "welcome"}>
            {welcome({
              setState,
              welcomeError,
              setWelcomeError,
            })}
          </Match>

          <Match when={state() === "setup"}>
            <div class={styles.setup}>
              <div class={styles.setupHeader}>
                <Button
                  hierarchy="secondary"
                  ghost={true}
                  icon="ArrowLeft"
                  onClick={() => setState("welcome")}
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

          <Match when={state() === "creating"}>
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
};
