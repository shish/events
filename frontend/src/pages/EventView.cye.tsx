/// <reference types="Cypress" />

import { randomUsername } from "../../cypress/support/commands";

export {};

describe("event", () => {
    it("view an event", () => {
        cy.login("demo", "demo");
        cy.visit("/event/1");
        // cy.get('[href^="/post/"]').first().click();
        //cy.contains("Privacy").should("exist");
    });
});
