export interface TableData {
  name: string;
  status: NodeStatusKeys;
  last_seen: number;
}

export const NodeStatus = {
  Online: "Online",
  Offline: "Offline",
  Pending: "Pending",
};

export type NodeStatusKeys = (typeof NodeStatus)[keyof typeof NodeStatus];

function createData(
  name: string,
  status: NodeStatusKeys,
  last_seen: number
): TableData {
  if (status == NodeStatus.Online) {
    last_seen = 0;
  }

  return {
    name,
    status,
    last_seen: last_seen,
  };
}

var nameNumber = 0;

// A function to generate random names
function getRandomName(): string {
  let names = [
    "Alice",
    "Bob",
    "Charlie",
    "David",
    "Eve",
    "Frank",
    "Grace",
    "Heidi",
    "Ivan",
    "Judy",
    "Mallory",
    "Oscar",
    "Peggy",
    "Sybil",
    "Trent",
    "Victor",
    "Walter",
    "Wendy",
    "Zoe",
  ];
  let index = Math.floor(Math.random() * names.length);
  return names[index] + nameNumber++;
}

// A function to generate random IPv6 addresses
// function getRandomId(): string {
//   let hex = "0123456789abcdef";
//   let id = "";
//   for (let i = 0; i < 8; i++) {
//     for (let j = 0; j < 4; j++) {
//       let index = Math.floor(Math.random() * hex.length);
//       id += hex[index];
//     }
//     if (i < 7) {
//       id += ":";
//     }
//   }
//   return id;
// }

// A function to generate random status keys
function getRandomStatus(): NodeStatusKeys {
  let statusKeys = [NodeStatus.Online, NodeStatus.Offline, NodeStatus.Pending];
  let index = Math.floor(Math.random() * statusKeys.length);
  return statusKeys[index];
}

// A function to generate random last seen values
function getRandomLastSeen(status: NodeStatusKeys): number {
  if (status === "online") {
    return 0;
  } else {
    let min = 1; // One day ago
    let max = 360; // One year ago
    return Math.floor(Math.random() * (max - min + 1) + min);
  }
}

export const tableData = [
  createData(
    "Matchbox",

    NodeStatus.Pending,
    0
  ),
  createData(
    "Ahorn",

    NodeStatus.Online,
    0
  ),
  createData(
    "Yellow",

    NodeStatus.Offline,
    16.0
  ),
  createData(
    "Rauter",

    NodeStatus.Offline,
    6.0
  ),
  createData(
    "Porree",

    NodeStatus.Offline,
    13
  ),
  createData(
    "Helsinki",

    NodeStatus.Online,
    0
  ),
  createData(
    "Kelle",

    NodeStatus.Online,
    0
  ),
  createData(
    "Shodan",

    NodeStatus.Online,
    0.0
  ),
  createData(
    "Qubasa",

    NodeStatus.Offline,
    7.0
  ),
  createData(
    "Green",

    NodeStatus.Offline,
    2
  ),
  createData("Gum", NodeStatus.Offline, 0),
  createData("Xu", NodeStatus.Online, 0),
  createData(
    "Zaatar",

    NodeStatus.Online,
    0
  ),
];

// A function to execute the createData function with dummy data in a loop 100 times and return an array
export function executeCreateData(): TableData[] {
  let result: TableData[] = [];
  for (let i = 0; i < 100; i++) {
    // Generate dummy data
    let name = getRandomName();
    let status = getRandomStatus();
    let last_seen = getRandomLastSeen(status);

    // Call the createData function and push the result to the array
    result.push(createData(name, status, last_seen));
  }
  return result;
}
