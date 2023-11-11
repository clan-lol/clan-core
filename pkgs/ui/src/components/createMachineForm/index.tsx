import { createMachine, setMachineConfig } from "@/api/machine/machine";
import {
  Box,
  Button,
  CircularProgress,
  LinearProgress,
  MobileStepper,
  Step,
  StepLabel,
  Stepper,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "react-hot-toast";
import { useAppState } from "../hooks/useAppContext";
import ClanModules from "./clanModules";
import { CustomConfig } from "./customConfig";
import { CreateMachineForm, FormStep } from "./interfaces";

export function CreateMachineForm() {
  const {
    data: { clanName },
  } = useAppState();
  const formHooks = useForm<CreateMachineForm>({
    defaultValues: {
      isSchemaLoading: false,
      name: "",
      config: {},
      modules: [],
    },
  });

  const { handleSubmit, watch } = formHooks;
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const [activeStep, setActiveStep] = useState<number>(0);

  const steps: FormStep[] = [
    {
      id: "modules",
      label: "Modules",
      content: clanName ? (
        <ClanModules clanName={clanName} formHooks={formHooks} />
      ) : (
        <LinearProgress />
      ),
    },
    {
      id: "config",
      label: "Customize",
      content: clanName ? (
        <CustomConfig formHooks={formHooks} clanName={clanName} />
      ) : (
        <LinearProgress />
      ),
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

  const currentStep = steps.at(activeStep);

  async function onSubmit(data: CreateMachineForm) {
    console.log({ data }, "Aggregated Data; creating machine from");
    if (clanName) {
      if (!data.name) {
        toast.error("Machine name should not be empty");
        return;
      }
      await createMachine(clanName, {
        name: data.name,
      });
      await setMachineConfig(clanName, data.name, {
        clan: data.config.formData,
        clanImports: data.modules,
      });
    }
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
          disabled={
            !formHooks.formState.isValid ||
            (activeStep == 0 && !watch("schema")?.type) ||
            watch("isSchemaLoading")
          }
          onClick={handleNext}
          color="secondary"
          startIcon={
            watch("isSchemaLoading") ? <CircularProgress /> : undefined
          }
        >
          {activeStep <= steps.length - 1 && "Next"}
        </Button>
      )}
      {activeStep === steps.length - 1 && (
        <Button color="secondary" type="submit">
          Save
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
            {steps.map(({ label }) => {
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
