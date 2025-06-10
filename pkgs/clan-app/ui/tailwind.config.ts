import kobalte from "@kobalte/tailwindcss";
import core from "./tailwind/core-plugin";

/** @type {import('tailwindcss').Config} */
const config = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {},
  plugins: [core, kobalte],
};

export default config;
