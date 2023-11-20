import { Button } from "@mui/material";
import Link from "next/link";

export default function Manage() {
  return (
    <div>
      Select
      <Button>
        <Link href="/manage/join">Join</Link>
      </Button>
      <Button>
        <Link href="/manage/create">Create</Link>
      </Button>
      <ul>
        <li>History</li>
        <li>Recent History</li>
        <li>Ancient History</li>
        <li>Cosmic History</li>
      </ul>
    </div>
  );
}
