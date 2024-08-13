const typography = require("@tailwindcss/typography");
const daisyui = require("daisyui");

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {},
  },
  daisyui: {
    themes: [
      {
        light_clan: {
          primary: "#29b1eb",
          secondary: "#4d6a6b",
          accent: "#37cdbe",
          neutral: "#3d4451",
          error: "#ff2c78",
          success: "#0ae856",
          warning: "#ffdd2c",
          "base-100": "#d1dadb",
        },
      },
    ],
  },
  plugins: [typography, daisyui],
};
