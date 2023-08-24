export interface TableData {
  name: string;
  id: string;
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
  id: string,
  status: NodeStatusKeys,
  last_seen: number,
): TableData {
  return {
    name,
    id,
    status,
    last_seen: last_seen,
  };
}

export const tableData = [
  createData(
    "Matchbox",
    "42:0:f21:6916:e333:c47e:4b5c:e74c",
    NodeStatus.Pending,
    0,
  ),
  createData(
    "Ahorn",
    "42:0:3c46:b51c:b34d:b7e1:3b02:8d24",
    NodeStatus.Online,
    0,
  ),
  createData(
    "Yellow",
    "42:0:3c46:98ac:9c80:4f25:50e3:1d8f",
    NodeStatus.Offline,
    16.0,
  ),
  createData(
    "Rauter",
    "42:0:61ea:b777:61ea:803:f885:3523",
    NodeStatus.Offline,
    6.0,
  ),
  createData(
    "Porree",
    "42:0:e644:4499:d034:895e:34c8:6f9a",
    NodeStatus.Offline,
    13,
  ),
  createData(
    "Helsinki",
    "42:0:3c46:fd4a:acf9:e971:6036:8047",
    NodeStatus.Online,
    0,
  ),
  createData(
    "Kelle",
    "42:0:3c46:362d:a9aa:4996:c78e:839a",
    NodeStatus.Online,
    0,
  ),
  createData(
    "Shodan",
    "42:0:3c46:6745:adf4:a844:26c4:bf91",
    NodeStatus.Online,
    0.0,
  ),
  createData(
    "Qubasa",
    "42:0:3c46:123e:bbea:3529:db39:6764",
    NodeStatus.Offline,
    7.0,
  ),
  createData(
    "Green",
    "42:0:a46e:5af:632c:d2fe:a71d:cde0",
    NodeStatus.Offline,
    2,
  ),
  createData("Gum", "42:0:e644:238d:3e46:c884:6ec5:16c", NodeStatus.Offline, 0),
  createData("Xu", "42:0:ca48:c2c2:19fb:a0e9:95b9:794f", NodeStatus.Online, 0),
  createData(
    "Zaatar",
    "42:0:3c46:156e:10b6:3bd6:6e82:b2cd",
    NodeStatus.Online,
    0,
  ),
];
