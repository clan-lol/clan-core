import { Chip } from "@mui/material";

interface FlakeBadgeProps {
  flakeUrl: string;
  flakeAttr: string;
}
export const FlakeBadge = (props: FlakeBadgeProps) => (
  <Chip
    color="secondary"
    label={`${props.flakeUrl}#${props.flakeAttr}`}
    sx={{
      p: 2,
      "&.MuiChip-root": {
        maxWidth: "unset",
      },
      "&.MuiChip-label": {
        overflow: "unset",
      },
    }}
  />
);
