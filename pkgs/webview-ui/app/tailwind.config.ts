import typography from "@tailwindcss/typography";
import core from "./tailwind/core-plugin";

/** @type {import('tailwindcss').Config} */
const config = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {},
  plugins: [typography, core],
};

export default config;
