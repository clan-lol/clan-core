import { RJSFSchema } from "@rjsf/utils";
export const schema: RJSFSchema = {
  properties: {
    bloatware: {
      properties: {
        age: {
          default: 42,
          description: "The age of the user",
          type: "integer",
        },
        isAdmin: {
          default: false,
          description: "Is the user an admin?",
          type: "boolean",
        },
        kernelModules: {
          default: ["nvme", "xhci_pci", "ahci"],
          description: "A list of enabled kernel modules",
          items: {
            type: "string",
          },
          type: "array",
        },
        name: {
          default: "John Doe",
          description: "The name of the user",
          type: "string",
        },
        services: {
          properties: {
            opt: {
              default: "foo",
              description: "A submodule option",
              type: "string",
            },
          },
          type: "object",
        },
        userIds: {
          additionalProperties: {
            type: "integer",
          },
          default: {
            albrecht: 3,
            horst: 1,
            peter: 2,
          },
          description: "Some attributes",
          type: "object",
        },
      },
      type: "object",
    },
    networking: {
      properties: {
        zerotier: {
          properties: {
            controller: {
              properties: {
                enable: {
                  default: false,
                  description:
                    "Whether to enable turn this machine into the networkcontroller.",
                  type: "boolean",
                },
                public: {
                  default: false,
                  description:
                    "everyone can join a public network without having the administrator to accept\n",
                  type: "boolean",
                },
              },
              type: "object",
            },
            networkId: {
              description: "zerotier networking id\n",
              type: "string",
            },
          },
          required: ["networkId"],
          type: "object",
        },
      },
      type: "object",
    },
  },
  type: "object",
};
