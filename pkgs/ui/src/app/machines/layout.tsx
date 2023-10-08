import { MachineContextProvider } from "@/components/hooks/useMachines";

export default function Layout({ children }: { children: React.ReactNode }) {
  return <MachineContextProvider>{children}</MachineContextProvider>;
}
