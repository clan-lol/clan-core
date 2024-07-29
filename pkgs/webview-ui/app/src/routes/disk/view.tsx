import { callApi } from "@/src/api";
import { activeURI } from "@/src/App";
import { createQuery } from "@tanstack/solid-query";
import { createEffect } from "solid-js";
import toast from "solid-toast";

export function DiskView() {
  const query = createQuery(() => ({
    queryKey: ["disk", activeURI()],
    queryFn: async () => {
      const currUri = activeURI();
      if (currUri) {
        // Example of calling an API
        const result = await callApi("get_inventory", { base_path: currUri });
        if (result.status === "error") throw new Error("Failed to fetch data");
        return result.data;
      }
    },
  }));
  createEffect(() => {
    // Example debugging the data
    console.log(query);
  });
  return (
    <div>
      <h1>Configure Disk</h1>
      <p>
        Select machine then configure the disk. Required before installing for
        the first time.
      </p>
    </div>
  );
}
