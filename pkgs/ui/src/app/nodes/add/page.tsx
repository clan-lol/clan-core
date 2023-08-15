"use client";
import React, { ReactNode, useEffect, useMemo, useState } from "react";
import {
  Box,
  Button,
  MenuItem,
  Select,
  Step,
  StepLabel,
  Stepper,
  Typography,
} from "@mui/material";
import {
  Control,
  Controller,
  Form,
  useForm,
  UseFormWatch,
} from "react-hook-form";
import { DashboardCard } from "@/components/card";
import Info from "@mui/icons-material/Info";
import { Check, Usb } from "@mui/icons-material";

import toast from "react-hot-toast";
import { buffer } from "stream/consumers";

type StepId = "select" | "create" | "install";

type Step = {
  id: StepId;
  label: string;
  children?: ReactNode;
};

const steps: Step[] = [
  {
    id: "select",
    label: "Image",
  },
  {
    id: "create",
    label: "Customize new template",
  },
  {
    id: "install",
    label: "Install",
  },
];

const serverImagesData = [
  {
    id: "1",
    name: "Cassies Gaming PC",
  },
  {
    id: "2",
    name: "Ivern office",
  },
  {
    id: "3",
    name: "Dad's working pc",
  },
  {
    id: "4",
    name: "Sisters's pony preset",
  },
];

interface StepContentProps {
  id: StepId;
  control: Control<FormValues>;
  watch: UseFormWatch<FormValues>;
}
const StepContent = (props: StepContentProps) => {
  const { id, control, watch } = props;

  const [hasWebUsb, setHasWebUsb] = useState<boolean>(false);
  useEffect(() => {
    setHasWebUsb(Boolean(navigator?.usb));
  }, []);

  const content: Record<StepId, ReactNode> = {
    select: (
      <div>
        <div className="">
          <Typography component="div" variant="overline" className="h-full">
            Select an image
          </Typography>
          <Controller
            name="image"
            control={control}
            render={({ field }) => (
              <Select
                {...field}
                defaultValue={control._defaultValues.image}
                fullWidth
              >
                {imageOptions.map(({ id, label }) => (
                  <MenuItem key={id} value={id}>
                    {label}
                  </MenuItem>
                ))}
              </Select>
            )}
          />
          <div className="w-full py-4">
            <DashboardCard title={<Info />}>
              <div className="w-full py-2">
                <Typography className="pb-4">
                  {watch("image") === "new"
                    ? `You selected the option to create a new system image. Configure your predefined options, such as programs, clans, etc. in
                the following steps.`
                    : `You selected the option to reuse an existing system image. Please select one
                from the list below`}
                </Typography>
                {watch("image") === "existing" && (
                  <Controller
                    name="source"
                    control={control}
                    render={({ field }) => (
                      <Select
                        {...field}
                        defaultValue={control._defaultValues.source}
                        fullWidth
                      >
                        {serverImagesData.map(({ id, name }) => (
                          <MenuItem key={id} value={id}>
                            {name}
                          </MenuItem>
                        ))}
                      </Select>
                    )}
                  />
                )}
              </div>
            </DashboardCard>
          </div>
        </div>
      </div>
    ),
    create: (
      <div className="flex w-full flex-col">
        <div className="my-3 w-full p-4">
          Formular generated from nix flake jsonschema
        </div>
      </div>
    ),
    install: (
      <div className="flex w-full justify-center">
        <Button
          color="secondary"
          type="submit"
          startIcon={<Usb />}
          variant="contained"
        >
          {hasWebUsb ? "Flash USB Device" : "Download installer image"}
        </Button>
      </div>
    ),
  };
  return (
    <div className="mt-4 flex p-4">
      <div className="flex w-full flex-col">
        <Typography
          component="div"
          variant="overline"
          className="flex w-full justify-center"
        >
          {watch("image") == "new"
            ? "Create system template"
            : "Choose existing"}
        </Typography>
        <div className="my-3 w-full p-4">{content[id]}</div>
      </div>
    </div>
  );
};

type FormValues = {
  image: ImageOption;
  source: string;
};
type ImageOption = "new" | "existing";

type ImageOptions = {
  id: ImageOption;
  label: string;
}[];
const imageOptions: ImageOptions = [
  {
    id: "new",
    label: "New image",
  },
  {
    id: "existing",
    label: "Previously created image",
  },
];

const defaultValues: FormValues = {
  image: "new",
  source: serverImagesData[0].id,
};

export default function AddNode() {
  const { handleSubmit, control, watch, reset, formState } =
    useForm<FormValues>({
      defaultValues,
    });

  const [activeStep, setActiveStep] = useState<number>(0);
  const [usb, setUsb] = useState<USB | undefined>(undefined);
  useEffect(() => {
    setUsb(navigator?.usb);
  }, []);

  const handleNext = () => {
    if (activeStep < visibleSteps.length - 1) {
      setActiveStep((prevActiveStep) => prevActiveStep + 1);
    }
  };

  const handleBack = () => {
    if (activeStep > 0) {
      setActiveStep((prevActiveStep) => prevActiveStep - 1);
    }
  };

  const handleReset = () => {
    setActiveStep(0);
    reset();
  };

  async function onSubmit(data: any) {
    console.log({ data }, "To be submitted");
    if (usb) {
      let device;
      try {
        device = await usb.requestDevice({
          filters: [{}],
        });
        toast.success(`Connected to '${device.productName}'`);
      } catch (error) {
        console.log({ error });
        toast.error("Couldn't connect to usb device");
      }
      if (device) {
        // await device.open();
        // await device.selectConfiguration(1);
        // await device.claimInterface(0);
        // const data = new Uint8Array([1, 2, 3]);
        // device.transferOut(2, data);
      }
    } else {
      //Offer the image as download

      const blob = new Blob(["data"]);
      let url = window.URL.createObjectURL(blob);
      let a = document.createElement("a");
      a.href = url;
      a.download = "image.iso";
      a.click();
    }
    return true;
  }

  const imageValue = watch("image");
  const visibleSteps = useMemo(
    () =>
      steps.filter((s) => {
        if (imageValue == "existing" && s.id == "create") {
          return false;
        }
        return true;
      }),
    [imageValue],
  );
  // console.log({})
  const currentStep = visibleSteps.at(activeStep);
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Box sx={{ width: "100%" }}>
        <Stepper activeStep={activeStep} color="secondary">
          {visibleSteps.map(({ label }, index) => {
            const stepProps: { completed?: boolean } = {};
            const labelProps: {
              optional?: React.ReactNode;
            } = {};
            return (
              <Step
                sx={{
                  ".MuiStepIcon-root.Mui-active": {
                    color: "secondary.main",
                  },
                  ".MuiStepIcon-root.Mui-completed": {
                    color: "secondary.main",
                  },
                }}
                key={label}
                {...stepProps}
              >
                <StepLabel {...labelProps}>{label}</StepLabel>
              </Step>
            );
          })}
        </Stepper>
        {activeStep === visibleSteps.length ? (
          <>
            <Typography variant="h5" sx={{ mt: 2, mb: 1 }}>
              Image succesfully downloaded
            </Typography>
            <Box sx={{ display: "flex", flexDirection: "row", pt: 2 }}>
              <Box sx={{ flex: "1 1 auto" }} />
              <Button color="secondary" onClick={handleReset}>
                Reset
              </Button>
            </Box>
          </>
        ) : (
          <>
            {currentStep && (
              <StepContent
                id={currentStep.id}
                control={control}
                watch={watch}
              />
            )}
            <Box sx={{ display: "flex", flexDirection: "row", pt: 2 }}>
              <Button
                color="secondary"
                disabled={activeStep === 0}
                onClick={handleBack}
                sx={{ mr: 1 }}
              >
                Back
              </Button>
              <Box sx={{ flex: "1 1 auto" }} />

              {activeStep !== visibleSteps.length - 1 && (
                <Button onClick={handleNext} color="secondary">
                  {activeStep <= visibleSteps.length - 1 && "Next"}
                </Button>
              )}
              {activeStep === visibleSteps.length - 1 && (
                <Button color="secondary" onClick={handleReset}>
                  Reset
                </Button>
              )}
            </Box>
          </>
        )}
      </Box>
    </form>
  );
}
