import Image from "next/image";
import {
  default as clanDark,
  default as clanLight,
} from "../../public/clan-dark.png";

export default function Background() {
  return (
    <div
      className={
        "fixed top-0 h-[100vh] w-[100vw] overflow-hidden opacity-10 blur-md dark:opacity-40"
      }
    >
      {
        <>
          <Image
            className="dark:hidden"
            alt="clan"
            src={clanLight}
            placeholder="blur"
            quality={100}
            fill
            sizes="100vw"
            style={{
              objectFit: "cover",
            }}
          />
          <Image
            className="hidden dark:block"
            alt="clan"
            src={clanDark}
            placeholder="blur"
            quality={100}
            fill
            sizes="100vw"
            style={{
              objectFit: "cover",
            }}
          />
        </>
      }
    </div>
  );
}
