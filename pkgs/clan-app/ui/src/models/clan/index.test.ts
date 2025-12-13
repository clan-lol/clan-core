import { createClansStoreFixture } from "@/src/tests/utils";
import { testEffect } from "@solidjs/testing-library";
import { createEffect } from "solid-js";
import { describe, test, vi } from "vitest";

vi.mock("../api", () => {
  return {
    default: {
      clan: {
        updateClanData() {
          return;
        },
      },
    },
  };
});

describe("clan", () => {
  test("update data", ({ expect }) => {
    return testEffect((done) => {
      const [[clan, clanMethods], [clans, clansMethods]] =
        createClansStoreFixture({
          all: [
            {
              id: "/clan",
              data: {
                name: "testclan",
              },
              dataSchema: {},
              machines: {},
              services: {},
              globalTags: {
                regular: [],
                special: [],
              },
            },
          ],
          activeIndex: 0,
        });
      createEffect((runNum: number) => {
        [
          () => {
            expect(clan().data.name).toStrictEqual("testclan");
            clanMethods.updateClanData({
              name: "foo",
            });
          },
          () => {
            expect(clan().data.name).toStrictEqual("foo");
            done();
          },
        ][runNum]?.();
        return runNum + 1;
      }, 0);
    });
  });
});
