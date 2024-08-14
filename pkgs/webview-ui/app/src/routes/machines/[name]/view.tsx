import { useParams } from "@solidjs/router";

export const MachineDetails = () => {
  const params = useParams();
  return <div>Machine Details: {params.id}</div>;
};
