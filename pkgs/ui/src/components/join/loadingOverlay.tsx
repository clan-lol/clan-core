import { LinearProgress, Typography } from "@mui/material";

interface LoadingOverlayProps {
  title: React.ReactNode;
  subtitle: React.ReactNode;
}
export const LoadingOverlay = (props: LoadingOverlayProps) => {
  const { title, subtitle } = props;
  return (
    <div className="w-full">
      <Typography variant="subtitle2">{title}</Typography>
      <LinearProgress className="mb-2 w-full" />
      <div className="grid w-full place-items-center">{subtitle}</div>
      <Typography variant="subtitle1"></Typography>
    </div>
  );
};
