import {
  createForm,
  FieldValues,
  getValues,
  setValue,
  SubmitHandler,
} from "@modular-forms/solid";
import { TextInput } from "@/src/Form/fields/TextInput";
import { Button } from "./components/Button/Button";
import { callApi } from "./api";
import { API } from "@/api/API";
import { createSignal, Match, Switch, For, Show } from "solid-js";
import { Typography } from "./components/Typography";
import { useQuery } from "@tanstack/solid-query";
import { makePersisted } from "@solid-primitives/storage";
import jsonSchema from "@/api/API.json";

interface APITesterForm extends FieldValues {
  endpoint: string;
  payload: string;
}

const ACTUAL_API_ENDPOINT_NAMES: (keyof API)[] = jsonSchema.required.map(
  (key) => key as keyof API,
);

export const ApiTester = () => {
  const [persistedTestData, setPersistedTestData] = makePersisted(
    createSignal<APITesterForm>(),
    {
      name: "_test_data",
      storage: localStorage,
    },
  );

  const [formStore, { Form, Field }] = createForm<APITesterForm>({
    initialValues: persistedTestData() || { endpoint: "", payload: "" },
  });

  const [endpointSearchTerm, setEndpointSearchTerm] = createSignal(
    getValues(formStore).endpoint || "",
  );
  const [showSuggestions, setShowSuggestions] = createSignal(false);

  const filteredEndpoints = () => {
    const term = endpointSearchTerm().toLowerCase();
    if (!term) return ACTUAL_API_ENDPOINT_NAMES;
    return ACTUAL_API_ENDPOINT_NAMES.filter((ep) =>
      ep.toLowerCase().includes(term),
    );
  };

  const query = useQuery(() => {
    const currentEndpoint = getValues(formStore).endpoint;
    const currentPayload = getValues(formStore).payload;
    const values = getValues(formStore);

    return {
      queryKey: ["api-tester", currentEndpoint, currentPayload],
      queryFn: async () => {
        return await callApi(
          values.endpoint as keyof API,
          JSON.parse(values.payload || "{}"),
        );
      },
      staleTime: Infinity,
      enabled: false,
    };
  });

  const handleSubmit: SubmitHandler<APITesterForm> = (values) => {
    console.log(values);
    setPersistedTestData(values);
    setEndpointSearchTerm(values.endpoint);
    query.refetch();

    const v = getValues(formStore);
    console.log(v);
  };
  return (
    <div class="p-2">
      <h1>API Tester</h1>
      <Form onSubmit={handleSubmit}>
        <div class="flex flex-col">
          <Field name="endpoint">
            {(field, fieldProps) => (
              <div class="relative">
                <TextInput
                  label={"endpoint"}
                  value={field.value || ""}
                  inputProps={{
                    ...fieldProps,
                    onInput: (e: Event) => {
                      if (fieldProps.onInput) {
                        (fieldProps.onInput as (ev: Event) => void)(e);
                      }
                      setEndpointSearchTerm(
                        (e.currentTarget as HTMLInputElement).value,
                      );
                      setShowSuggestions(true);
                    },
                    onBlur: (e: FocusEvent) => {
                      if (fieldProps.onBlur) {
                        (fieldProps.onBlur as (ev: FocusEvent) => void)(e);
                      }
                      setTimeout(() => setShowSuggestions(false), 150);
                    },
                    onFocus: (e: FocusEvent) => {
                      setEndpointSearchTerm(field.value || "");
                      setShowSuggestions(true);
                    },
                    onKeyDown: (e: KeyboardEvent) => {
                      if (e.key === "Escape") {
                        setShowSuggestions(false);
                      }
                    },
                  }}
                />
                <Show
                  when={showSuggestions() && filteredEndpoints().length > 0}
                >
                  <ul class="absolute z-10 w-full bg-white border border-gray-300 rounded mt-1 max-h-60 overflow-y-auto shadow-lg">
                    <For each={filteredEndpoints()}>
                      {(ep) => (
                        <li
                          class="p-2 hover:bg-gray-100 cursor-pointer"
                          onMouseDown={(e) => {
                            e.preventDefault();
                            setValue(formStore, "endpoint", ep);
                            setEndpointSearchTerm(ep);
                            setShowSuggestions(false);
                          }}
                        >
                          {ep}
                        </li>
                      )}
                    </For>
                  </ul>
                </Show>
              </div>
            )}
          </Field>
          <Field name="payload">
            {(field, fieldProps) => (
              <TextInput
                label={"payload"}
                value={field.value || ""}
                inputProps={fieldProps}
              />
            )}
          </Field>
          <Button class="m-2" disabled={query.isFetching}>
            Send
          </Button>
        </div>
      </Form>
      <div>
        <Typography hierarchy="title" size="default">
          Result
        </Typography>
        <Switch>
          <Match when={query.isFetching}>
            <span>loading ...</span>
          </Match>
          <Match when={query.isFetched}>
            <pre>
              <code>{JSON.stringify(query.data, null, 2)}</code>
            </pre>
          </Match>
        </Switch>
      </div>
    </div>
  );
};
