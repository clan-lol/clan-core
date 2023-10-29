import { MachineContextProvider } from "@/components/hooks/useMachines";

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    // TODO: select flake?
    <MachineContextProvider flakeName="defaultFlake">
      {children}
    </MachineContextProvider>
  );
}
