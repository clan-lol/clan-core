"use client";
import { useAppState } from "@/components/hooks/useAppContext";
import { MachineContextProvider } from "@/components/hooks/useMachines";

export default function Layout({ children }: { children: React.ReactNode }) {
  const {
    data: { clanName },
  } = useAppState();
  return (
    <>
      {clanName && (
        <MachineContextProvider flakeName={clanName}>
          {children}
        </MachineContextProvider>
      )}
    </>
  );
}
