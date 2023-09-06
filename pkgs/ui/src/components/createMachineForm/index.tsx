import {
  Box,
  Button,
  MobileStepper,
  Step,
  StepLabel,
  Stepper,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import React, { ReactNode, useState } from "react";
import { useForm, UseFormReturn } from "react-hook-form";
import { CustomConfig } from "./customConfig";
import { CreateMachineForm, FormStep } from "./interfaces";

const SC = (props: { children: ReactNode }) => {
  return <>{props.children}</>;
};

export function CreateMachineForm() {
  const formHooks = useForm<CreateMachineForm>({
    defaultValues: {
      name: "",
      config: {},
    },
  });
  const { handleSubmit, control, watch, reset, formState } = formHooks;
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const [activeStep, setActiveStep] = useState<number>(0);

  const steps: FormStep[] = [
    {
      id: "template",
      label: "Template",
      content: <div></div>,
    },
    {
      id: "modules",
      label: "Modules",
      content: <div></div>,
    },
    {
      id: "config",
      label: "Customize",
      content: <CustomConfig formHooks={formHooks} />,
    },
    {
      id: "save",
      label: "Save",
      content: <div></div>,
    },
  ];

  const handleNext = () => {
    if (activeStep < steps.length - 1) {
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
  const currentStep = steps.at(activeStep);

  async function onSubmit(data: any) {
    console.log({ data }, "Aggregated Data; creating machine from");
  }

  const BackButton = () => (
    <Button
      color="secondary"
      disabled={activeStep === 0}
      onClick={handleBack}
      sx={{ mr: 1 }}
    >
      Back
    </Button>
  );

  const NextButton = () => (
    <>
      {activeStep !== steps.length - 1 && (
        <Button
          disabled={!formHooks.formState.isValid}
          onClick={handleNext}
          color="secondary"
        >
          {activeStep <= steps.length - 1 && "Next"}
        </Button>
      )}
      {activeStep === steps.length - 1 && (
        <Button color="secondary" onClick={handleReset}>
          Reset
        </Button>
      )}
    </>
  );
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Box sx={{ width: "100%" }}>
        {isMobile && (
          <MobileStepper
            activeStep={activeStep}
            color="secondary"
            backButton={<BackButton />}
            nextButton={<NextButton />}
            steps={steps.length}
          />
        )}
        {!isMobile && (
          <Stepper activeStep={activeStep} color="secondary">
            {steps.map(({ label }, index) => {
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
        )}
        {/* <CustomConfig formHooks={formHooks} /> */}
        {/* The step Content */}
        {currentStep && currentStep.content}

        {/* Desktop step controls */}
        {!isMobile && (
          <Box sx={{ display: "flex", flexDirection: "row", pt: 2 }}>
            <BackButton />
            <Box sx={{ flex: "1 1 auto" }} />
            <NextButton />
          </Box>
        )}
      </Box>
    </form>
  );
}
