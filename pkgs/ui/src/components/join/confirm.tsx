"use client";
import { useState } from "react";
import { LoadingOverlay } from "./loadingOverlay";
import { FlakeBadge } from "../flakeBadge/flakeBadge";
import { Typography, Button } from "@mui/material";
// import { FlakeResponse } from "@/api/model";
import { ConfirmVM } from "./confirmVM";
import { Log } from "./log";
import GppMaybeIcon from "@mui/icons-material/GppMaybe";
import { useInspectFlake } from "@/api/default/default";

interface ConfirmProps {
  flakeUrl: string;
  flakeAttr: string;
  handleBack: () => void;
}
export const Confirm = (props: ConfirmProps) => {
  const { flakeUrl, handleBack, flakeAttr } = props;
  const [userConfirmed, setUserConfirmed] = useState(false);

  const { data, isLoading } = useInspectFlake({
    url: flakeUrl,
  });

  return userConfirmed ? (
    <ConfirmVM
      url={flakeUrl}
      handleBack={handleBack}
      defaultFlakeAttr={flakeAttr}
    />
  ) : (
    <div className="mb-2 flex w-full max-w-2xl flex-col items-center justify-self-center pb-2 ">
      {isLoading && (
        <LoadingOverlay
          title={"Loading Flake"}
          subtitle={<FlakeBadge flakeUrl={flakeUrl} flakeAttr={flakeAttr} />}
        />
      )}
      {data && (
        <>
          <Typography variant="subtitle1">
            To join the clan you must trust the Author
          </Typography>
          <GppMaybeIcon sx={{ height: "10rem", width: "10rem", mb: 5 }} />
          <Button
            autoFocus
            size="large"
            color="warning"
            variant="contained"
            onClick={() => setUserConfirmed(true)}
            sx={{ mb: 10 }}
          >
            Trust Flake Author
          </Button>
          <Log
            title="What's about to be built"
            lines={data.data.content.split("\n")}
          />
        </>
      )}
    </div>
  );
};
