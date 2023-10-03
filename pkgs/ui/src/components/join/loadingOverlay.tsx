"use client";
import { CircularProgress, LinearProgress, Typography } from "@mui/material";

interface LoadingOverlayProps {
  title: React.ReactNode;
  subtitle: React.ReactNode;
  variant?: "linear" | "circle";
}
export const LoadingOverlay = (props: LoadingOverlayProps) => {
  const { title, subtitle, variant = "linear" } = props;
  return (
    <div className="w-full">
      <div className="grid w-full place-items-center">
        <Typography variant="subtitle1">{title}</Typography>
      </div>
      <div className="grid w-full place-items-center">
        <Typography variant="subtitle2">{subtitle}</Typography>
      </div>
      {variant === "linear" && <LinearProgress className="my-2 w-full" />}
      {variant === "circle" && (
        <div className="grid w-full place-items-center">
          <CircularProgress className="my-2 w-full" />
        </div>
      )}
    </div>
  );
};
