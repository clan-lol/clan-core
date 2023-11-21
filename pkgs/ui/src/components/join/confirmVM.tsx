"use client";

interface ConfirmVMProps {
  url: string;
  handleBack: () => void;
  defaultFlakeAttr: string;
}

export function ConfirmVM(props: ConfirmVMProps) {
  return (
    <div className="mb-2 flex w-full max-w-2xl flex-col items-center justify-self-center pb-2"></div>
  );
}
