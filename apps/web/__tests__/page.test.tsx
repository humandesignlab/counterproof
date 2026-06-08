import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import Home from "../app/page";

test("home page renders the Counterproof heading", () => {
  render(<Home />);
  expect(screen.getByRole("heading", { name: "Counterproof" })).toBeDefined();
});
