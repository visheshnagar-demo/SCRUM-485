// AUTO-MANAGED smoke test (added only when the project had no tests).
// Importing App exercises the whole module graph, so this fails if any
// component it pulls in is broken. Replace with real component tests.
import { describe, it, expect } from "vitest";
import App from "./App";

describe("smoke", () => {
  it("App module loads without throwing", () => {
    expect(App).toBeDefined();
  });
});
