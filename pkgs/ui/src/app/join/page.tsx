"use client";
import React, { useState } from "react";
import { Button, Paper, Typography } from "@mui/material";
import { useSearchParams } from "next/navigation";
import GppMaybeIcon from "@mui/icons-material/GppMaybe";
import { useInspectFlake } from "@/api/default/default";
import { ConfirmVM } from "@/components/join/join";
import { LoadingOverlay } from "@/components/join/loadingOverlay";
import { FlakeBadge } from "@/components/flakeBadge/flakeBadge";
import { Log } from "@/components/join/log";

export default function Page() {
  const queryParams = useSearchParams();
  const flakeUrl = queryParams.get("flake") || "";
  const flakeAttribute = queryParams.get("attr") || "default";
  const [userConfirmed, setUserConfirmed] = useState(false);

  const clanName = "Lassul.us";

  const { data, error, isLoading } = useInspectFlake({ url: flakeUrl });

  return (
    <div className="grid h-[70vh] w-full place-items-center gap-y-4">
      <Typography variant="h4" className="w-full text-center">
        Join{" "}
        <Typography variant="h4" className="font-bold" component={"span"}>
          {clanName}
        </Typography>
        {"' "}
        Clan
      </Typography>

      {flakeUrl && flakeAttribute ? (
        userConfirmed ? (
          <ConfirmVM url={flakeUrl} attr={flakeAttribute} clanName={clanName} />
        ) : (
          <div className="mb-2 flex w-full max-w-xl flex-col items-center pb-2">
            {isLoading && (
              <LoadingOverlay
                title={"Loading Flake"}
                subtitle={
                  <FlakeBadge flakeUrl={flakeUrl} flakeAttr={flakeAttribute} />
                }
              />
            )}
            {data && (
              <>
                <Typography variant="subtitle1">
                  To build the VM you must trust the Author of this Flake
                </Typography>
                <GppMaybeIcon sx={{ height: "10rem", width: "10rem", mb: 5 }} />
                <Button
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
        )
      ) : (
        <div>Invalid URL</div>
      )}
    </div>
  );
}
