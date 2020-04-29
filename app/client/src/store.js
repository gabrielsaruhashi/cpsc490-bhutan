import { createStore, combineReducers, applyMiddleware, compose } from "redux";
import keplerGlReducer from "kepler.gl/reducers";
import { enhanceReduxMiddleware } from "kepler.gl/middleware";
import thunk from "redux-thunk";
import logger from "redux-logger";

const initialState = {};
const reducers = combineReducers({
  // <-- mount kepler.gl reducer in your app
  keplerGl: keplerGlReducer
});

const middlewares = enhanceReduxMiddleware([thunk, logger]);

export const enhancers = [applyMiddleware(...middlewares)];

//  add redux devtools
const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;

// using createStore
export default function configureStore() {
  return createStore(reducers, initialState, composeEnhancers(...enhancers));
}
