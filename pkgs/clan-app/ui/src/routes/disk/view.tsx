import { callApi } from "@/src/api";
import { useQuery } from "@tanstack/solid-query";
import { useClanContext } from "@/src/contexts/clan";

export function DiskView() {
  const { activeClanURI } = useClanContext();

  const query = useQuery(() => ({
    queryKey: ["disk", activeClanURI()],
    queryFn: async () => {
      const currUri = activeClanURI();
      if (currUri) {
        // Example of calling an API
        const result = await callApi("get_inventory", {
          flake: { identifier: currUri },
        });
        if (result.status === "error") throw new Error("Failed to fetch data");
        return result.data;
      }
    },
  }));
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
