"use client";
import { useAppState } from "@/components/hooks/useAppContext";
import { MachineContextProvider } from "@/components/hooks/useMachines";

export default function Layout({ children }: { children: React.ReactNode }) {
  const {
    data: { clanDir },
  } = useAppState();
  return (
    <>
      {!clanDir && <div>No clan selected</div>}
      {clanDir && (
        <MachineContextProvider clanDir={clanDir}>
          {children}
        </MachineContextProvider>
      )}
    </>
  );
}
