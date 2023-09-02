import { RJSFSchema } from "@rjsf/utils";
export const schema: RJSFSchema = {
  type: "object",
  properties: {
    name: {
      type: "string",
      default: "John-nixi",
      description: "The name of the machine",
    },
    age: {
      type: "integer",
      default: 42,
      description: "The age of the user",
      maximum: 40,
    },
    role: {
      enum: ["New York", "Amsterdam", "Hong Kong"],
      description: "Role of the user",
    },
    kernelModules: {
      type: "array",
      items: {
        type: "string",
      },
      default: ["nvme", "xhci_pci", "ahci"],
      description: "A list of enabled kernel modules",
    },
    userIds: {
      type: "array",
      items: {
        type: "object",
        properties: {
          user: {
            type: "string",
          },
          id: {
            type: "integer",
          },
        },
      },
      default: [
        {
          user: "John",
          id: 12,
        },
      ],
      description: "Some attributes",
    },
    xdg: {
      type: "object",
      properties: {
        portal: {
          type: "object",
          properties: {
            xdgOpenUsePortal: {
              type: "boolean",
              default: false,
            },
            enable: {
              type: "boolean",
              default: false,
            },
            lxqt: {
              type: "object",
              properties: {
                enable: {
                  type: "boolean",
                  default: false,
                },
                styles: {
                  type: "array",
                  items: {
                    type: "string",
                  },
                },
              },
            },
            extraPortals: {
              type: "array",
              items: {
                type: "string",
              },
            },
            wlr: {
              type: "object",
              properties: {
                enable: {
                  type: "boolean",
                  default: false,
                },
                settings: {
                  type: "object",
                  default: {
                    screencast: {
                      output_name: "HDMI-A-1",
                      max_fps: 30,
                      exec_before: "disable_notifications.sh",
                      exec_after: "enable_notifications.sh",
                      chooser_type: "simple",
                      chooser_cmd: "${pkgs.slurp}/bin/slurp -f %o -or",
                    },
                  },
                },
              },
            },
          },
        },
      },
    },
  },
};
