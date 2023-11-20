import Link from "next/link";

export default function Manage() {
  return (
    <div>
      Select
      <Link href="/manage/join">Join</Link>
      <Link href="/manage/create">Create</Link>
    </div>
  );
}
