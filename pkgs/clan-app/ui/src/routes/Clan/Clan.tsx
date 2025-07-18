import { RouteSectionProps } from "@solidjs/router";
import { Component, createEffect, JSX } from "solid-js";
import { useClanURI } from "@/src/hooks/clan";
import { CubeScene } from "@/src/scene/cubes";
import { MachinesQueryResult, useMachinesQuery } from "@/src/queries/queries";
import { callApi } from "@/src/hooks/api";
import { store, setStore } from "@/src/stores/clan";
import { produce } from "solid-js/store";
import { Button } from "@/src/components/Button/Button";

export const Clan: Component<RouteSectionProps> = (props) => {
  return (
    <>
      <div
        style={{
          position: "absolute",
          top: 0,
        }}
      >
        {props.children}
      </div>
      <ClanSceneController />
    </>
  );
};

const ClanSceneController = () => {
  const clanURI = useClanURI({ force: true });

  const onCreate = async (id: string) => {
    const api = callApi("create_machine", {
      opts: {
        clan_dir: {
          identifier: clanURI,
        },
        machine: {
          name: id,
        },
      },
    });
    const res = await api.result;
    if (res.status === "error") {
      // TODO: Handle displaying errors
      console.error("Error creating machine:");

      // Important: rejects the promise
      throw new Error(res.errors[0].message);
    }
    return;
  };

  createEffect(() => {
    console.log("sceneData changed:", store.sceneData);
  });

  return (
    <SceneDataProvider clanURI={clanURI}>
      {({ query }) => {
        return (
          <>
            <div
              class="flex flex-row"
              style={{ position: "absolute", top: "10px", left: "10px" }}
            >
              <Button
                ghost
                onClick={() => {
                  setStore(
                    produce((s) => {
                      for (const machineId in s.sceneData[clanURI]) {
                        // Reset the position of each machine to [0, 0]
                        // delete s.sceneData[clanURI][machineId];
                      }
                    }),
                  );
                }}
              >
                Reset Store
              </Button>
              <Button
                ghost
                onClick={() => {
                  console.log("Refetching API");
                  query.refetch();
                }}
              >
                Refetch API
              </Button>
            </div>
            <CubeScene
              cubesQuery={query}
              onCreate={onCreate}
              sceneStore={() => {
                const clanURI = useClanURI({ force: true });
                return store.sceneData?.[clanURI];
              }}
              setMachinePos={(machineId: string, pos: [number, number]) => {
                console.log("calling setStore", machineId, pos);
                setStore(
                  produce((s) => {
                    if (!s.sceneData) {
                      s.sceneData = {};
                    }
                    if (!s.sceneData[clanURI]) {
                      s.sceneData[clanURI] = {};
                    }
                    if (!s.sceneData[clanURI][machineId]) {
                      s.sceneData[clanURI][machineId] = { position: pos };
                    } else {
                      s.sceneData[clanURI][machineId].position = pos;
                    }
                  }),
                );
              }}
            />
          </>
        );
      }}
    </SceneDataProvider>
  );
};

const SceneDataProvider = (props: {
  clanURI: string | null;
  children: (sceneData: { query: MachinesQueryResult }) => JSX.Element;
}) => {
  const machinesQuery = useMachinesQuery({ clanURI: props.clanURI });

  // This component can be used to provide scene data or context if needed
  return props.children({ query: machinesQuery });
};
