import React from "react";
import ReactDOM from "react-dom";
import "./index.css";
import App from "./App";
import * as serviceWorker from "./serviceWorker";
import { Provider } from "react-redux";
import configureStore from "./store";

import "circular-std";

import { createMuiTheme, ThemeProvider } from "@material-ui/core/styles";

const CircularStd = {
  fontFamily: "CircularStd",
  fontStyle: "normal",
  fontDisplay: "swap",
  fontWeight: 400,
  src: `
    local('CircularStd'),
  `,
  unicodeRange:
    "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF"
};
const theme = createMuiTheme({
  typography: {
    fontFamily: "CircularStd"
  },
  overrides: {
    MuiCssBaseline: {
      "@global": {
        "@font-face": [CircularStd]
      }
    }
  }
});
ReactDOM.render(
  <ThemeProvider theme={theme}>
    <Provider store={configureStore()}>
      <App />
    </Provider>
  </ThemeProvider>,
  document.getElementById("root")
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
