import { Component, createSignal, Match, Setter, Show, Switch } from "solid-js";
import { RouteSectionProps, useNavigate } from "@solidjs/router";
import "./Onboarding.css";
import { Typography } from "@/src/components/Typography/Typography";
import { Button } from "@/src/components/Button/Button";
import { Divider } from "@/src/components/Divider/Divider";
import { Logo } from "@/src/components/Logo/Logo";
import { navigateToClan, selectClanFolder } from "@/src/hooks/clan";
import { activeClanURI } from "@/src/stores/clan";
import {
  createForm,
  FormStore,
  getError,
  getErrors,
  getValue,
  valiForm,
} from "@modular-forms/solid";
import { TextInput } from "@/src/components/Form/TextInput";
import { TextArea } from "@/src/components/Form/TextArea";
import { Fieldset } from "@/src/components/Form/Fieldset";
import * as v from "valibot";
import { HostFileInput } from "@/src/components/Form/HostFileInput";

type State = "welcome" | "setup";

const SetupSchema = v.object({
  name: v.pipe(v.string(), v.nonEmpty("Please enter a name.")),
  description: v.pipe(v.string(), v.nonEmpty("Please describe your clan.")),
  directory: v.pipe(v.string(), v.nonEmpty("Please select a directory.")),
});

type SetupForm = v.InferInput<typeof SetupSchema>;

interface backgroundProps {
  state: State;
  form: FormStore<SetupForm>;
}

const background = (props: backgroundProps) => (
  <div class="background">
    <div class="layer-1" />
    <div class="layer-2" />
    <div class="layer-3" />
    <Logo variant="Darknet" inverted={true} />
    <Logo variant="Clan" inverted={true} />
    <Show when={props.state === "setup"}>
      <div class="darknet-info">
        <Typography
          class="darknet-label"
          hierarchy="label"
          family="mono"
          size="default"
          color="inherit"
          weight="medium"
          inverted={true}
        >
          Your Darknet:
        </Typography>
        <Typography
          class="darknet-name"
          hierarchy="teaser"
          size="default"
          color="inherit"
          weight="medium"
          inverted={true}
        >
          {getValue(props.form, "name")}
        </Typography>
      </div>
    </Show>
  </div>
);

const welcome = (setState: Setter<State>) => {
  const navigate = useNavigate();

  const selectFolder = async () => {
    const uri = await selectClanFolder();
    navigateToClan(navigate, uri);
  };

  return (
    <div class="welcome">
      <Typography
        hierarchy="headline"
        size="xxl"
        weight="bold"
        align="center"
        inverted={true}
      >
        Build your <br />
        own darknet
      </Typography>
      <Button hierarchy="secondary" onClick={() => setState("setup")}>
        Start building
      </Button>
      <div class="separator">
        <Divider orientation="horizontal" inverted={true} />
        <Typography
          hierarchy="body"
          size="s"
          weight="medium"
          inverted={true}
          align="center"
        >
          or
        </Typography>
        <Divider orientation="horizontal" inverted={true} />
      </div>
      <Button hierarchy="primary" ghost={true} onAction={selectFolder}>
        Select folder
      </Button>
    </div>
  );
};

export const Onboarding: Component<RouteSectionProps> = (props) => {
  const navigate = useNavigate();

  const activeURI = activeClanURI();
  if (activeURI) {
    // the user has already selected a clan, so we should navigate to it
    console.log("active clan detected, navigating to it", activeURI);
    navigateToClan(navigate, activeURI);
  }

  const [state, setState] = createSignal<State>("welcome");

  const [setupForm, { Form, Field }] = createForm<SetupForm>({
    validate: valiForm(SetupSchema),
  });

  const metaError = () => {
    const errors = getErrors(setupForm, ["name", "description"]);
    return errors ? errors.name || errors.description : undefined;
  };

  return (
    <main id="welcome">
      {background({ form: setupForm, state: state() })}
      <div class="container">
        <Switch>
          <Match when={state() === "welcome"}>{welcome(setState)}</Match>

          <Match when={state() === "setup"}>
            <div class="setup">
              <div class="header">
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
              <Form>
                <Fieldset name="meta" error={metaError()}>
                  <Field name="name">
                    {(field, input) => (
                      <TextInput
                        {...field}
                        label="Name"
                        value={field.value}
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
                  <Divider inverted={true} />
                  <Field name="description">
                    {(field, input) => (
                      <TextArea
                        {...field}
                        value={field.value}
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

                <Fieldset
                  name="location"
                  error={getError(setupForm, "directory")}
                >
                  <Field name="directory">
                    {(field, input) => (
                      <HostFileInput
                        onSelectFile={async () => "test"}
                        {...field}
                        label="Select directory"
                        orientation="horizontal"
                        required={true}
                        validationState={
                          getError(setupForm, "directory") ? "invalid" : "valid"
                        }
                        input={input}
                      />
                    )}
                  </Field>
                </Fieldset>

                <div class="form-controls">
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
        </Switch>
      </div>
    </main>
  );
};
