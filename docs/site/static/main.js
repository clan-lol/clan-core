

let preferDarkTheme = prefersDarkMode();
let theme = localStorage.getItem('theme');
if (theme !== null) {
  setColorTheme(theme);
} else {
  setColorTheme(preferDarkTheme ? "dark" : "light");
}

// Get the media query list object for the prefers-color-scheme media feature
const colorSchemeQueryList = window.matchMedia("(prefers-color-scheme: dark)");
// Add an event listener for the change event
colorSchemeQueryList.addEventListener("change", handleColorSchemeChange);


function setColorTheme(theme) {
  if (theme === "dark") {
    document.body.setAttribute('data-md-color-scheme', 'slate');
    document.body.setAttribute('data-md-color-media', '(prefers-color-scheme: dark)')
    localStorage.setItem('theme', 'dark');
  } else {
    document.body.setAttribute('data-md-color-scheme', 'default');
    document.body.setAttribute('data-md-color-media', '(prefers-color-scheme: light)')
    localStorage.setItem('theme', 'light');
  }
}

// A function that returns true if the user prefers dark mode, false otherwise
function prefersDarkMode() {
  // Check if the browser supports the prefers-color-scheme media query
  if (window.matchMedia) {
    // Get the current value of the media query
    let colorScheme = window.matchMedia("(prefers-color-scheme: dark)");
    // Return true if the media query matches, false otherwise
    return colorScheme.matches;
  } else {
    // If the browser does not support the media query, return false by default
    return false;
  }
}

// A function that executes some logic based on the color scheme preference
function handleColorSchemeChange(e) {
  if (e.matches) {
    // The user prefers dark mode
    setColorTheme("dark");
  } else {
    // The user prefers light mode
    setColorTheme("light");
  }
}

// Detects if user pressed on the "change theme" button
document.addEventListener('DOMContentLoaded', function () {
  function handleThemeChange() {
    const isDarkMode = document.body.getAttribute('data-md-color-media').includes('dark');
    console.log(`Theme is now ${isDarkMode ? 'dark' : 'light'}`);

    // Detect the current theme
  }

  // Initial check
  handleThemeChange();

  // MutationObserver to detect changes to the `data-md-color-scheme` attribute
  const observer = new MutationObserver(handleThemeChange);
  observer.observe(document.body, {
    attributes: true,
    attributeFilter: ['data-md-color-media']
  });
});
