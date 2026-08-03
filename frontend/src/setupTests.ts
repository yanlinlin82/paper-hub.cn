import "@testing-library/jest-dom";

// Node >= 26 exposes experimental global `localStorage`/`sessionStorage`
// accessors that return `undefined` unless `--localstorage-file` is provided.
// Vitest's jsdom environment does not replace these (they are not part of its
// global key list), so restore the working jsdom implementations explicitly.
const jsdomWindow = (globalThis as { jsdom?: { window: Window } }).jsdom?.window;
if (jsdomWindow) {
  Object.defineProperty(globalThis, "localStorage", {
    value: jsdomWindow.localStorage,
    writable: true,
    configurable: true,
  });
  Object.defineProperty(globalThis, "sessionStorage", {
    value: jsdomWindow.sessionStorage,
    writable: true,
    configurable: true,
  });
}
