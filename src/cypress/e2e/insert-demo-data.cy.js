describe('Insert demo data in Administration', () => {
    it('should insert 5 demo records and update table when button is clicked', () => {
        cy.visit('http://127.0.0.1:8050');
        cy.wait(2000);

        // First clear database to have a clean state
        cy.get('#delete-database-button').should('exist').scrollIntoView();
        cy.on('window:confirm', () => true);
        cy.get('#delete-database-button').click();
        cy.wait(2000);

        // Verify table is empty
        cy.get('#saved-penguins-table .dash-spreadsheet-inner tbody tr td[data-dash-column="timestamp"]').should('not.exist');

        // Click insert demo data button
        cy.get('#insert-demo-data-button').should('exist').scrollIntoView().click();

        // Wait for the request to complete
        cy.wait(2000);

        // Now verify the table has exactly 5 data rows
        cy.get('#saved-penguins-table .dash-spreadsheet-inner tbody tr td[data-dash-column="timestamp"]').should('have.length', 5);
    });
});
