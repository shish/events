/// <reference types="Cypress" />

export {};

describe("event list", () => {
    it("show description", () => {
        cy.visit("/");
        cy.contains("Index").should("exist");
    });
    it("list events", () => {
        cy.visit("/");
        cy.contains("Events").should("exist");
    });
});
