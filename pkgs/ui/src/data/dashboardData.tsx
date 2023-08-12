export const status = {
  online: "online",
  offline: "offline",
  pending: "pending",
} as const;
// Convert object keys in a union type
export type Status = (typeof status)[keyof typeof status];

export type Network = {
  name: string;
  id: string;
};

export type ClanDevice = {
  id: string;
  name: string;
  status: Status;
  ipv6: string;
  networks: Network[];
};

export type ClanStatus = {
  self: ClanDevice;
  other: ClanDevice[];
};
export const clanStatus: ClanStatus = {
  self: {
    id: "1",
    name: "My Computer",
    ipv6: "",
    status: "online",
    networks: [
      {
        name: "Family",
        id: "1",
      },
      {
        name: "Fight-Club",
        id: "1",
      },
    ],
  },
  // other: [],
  other: [
    {
      id: "2",
      name: "Daddies Computer",
      status: "online",
      networks: [
        {
          name: "Family",
          id: "1",
        },
      ],
      ipv6: "",
    },
    {
      id: "3",
      name: "Lars Notebook",
      status: "offline",
      networks: [
        {
          name: "Family",
          id: "1",
        },
      ],
      ipv6: "",
    },
    {
      id: "4",
      name: "Cassie Computer",
      status: "pending",
      networks: [
        {
          name: "Family",
          id: "1",
        },
        {
          name: "Fight-Club",
          id: "2",
        },
      ],
      ipv6: "",
    },
    {
      id: "5",
      name: "Chuck Norris Computer",
      status: "online",
      networks: [
        {
          name: "Fight-Club",
          id: "2",
        },
      ],
      ipv6: "",
    },
    {
      id: "6",
      name: "Ella Bright",
      status: "pending",
      networks: [
        {
          name: "Fight-Club",
          id: "2",
        },
      ],
      ipv6: "",
    },
    {
      id: "7",
      name: "Ryan Flabberghast",
      status: "offline",
      networks: [
        {
          name: "Fight-Club",
          id: "2",
        },
      ],
      ipv6: "",
    },
  ],
};

export const severity = {
  info: "info",
  success: "success",
  warning: "warning",
  error: "error",
} as const;
// Convert object keys in a union type
export type Severity = (typeof severity)[keyof typeof severity];

export type Notification = {
  id: string;
  msg: string;
  source: string;
  date: string;
  severity: Severity;
};

export const notificationData: Notification[] = [
  {
    id: "1",
    date: "2022-12-27 08:26:49.219717",
    severity: "success",
    msg: "Defeated zombie mob flawless",
    source: "Chuck Norris Computer",
  },
  {
    id: "2",
    date: "2022-12-27 08:26:49.219717",
    severity: "error",
    msg: "Application Crashed: my little pony",
    source: "Cassie Computer",
  },
  {
    id: "3",
    date: "2022-12-27 08:26:49.219717",
    severity: "warning",
    msg: "Security update necessary",
    source: "Daddies Computer",
  },
  {
    id: "4",
    date: "2022-12-27 08:26:49.219717",
    severity: "info",
    msg: "Decompressed snowflakes",
    source: "My Computer",
  },
];
