"use client";
interface LogOptions {
  lines: string[];
  title?: string;
}
export const Log = (props: LogOptions) => {
  const { lines, title } = props;
  return (
    <div className="max-h-[70vh] min-h-[9rem] w-full overflow-scroll bg-neutral-20 p-4 text-white shadow-inner shadow-black">
      <div className="mb-1 text-neutral-70">{title}</div>
      <pre className="max-w-[90vw] text-xs">
        {lines.map((item, idx) => (
          <code key={`${idx}`} className="mb-2 block break-words">
            {item}
          </code>
        ))}
      </pre>
    </div>
  );
};
