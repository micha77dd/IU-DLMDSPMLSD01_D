describe('Delete database in Administration', () => {
    it('should delete all database entries when delete database button is confirmed', () => {
        cy.visit('http://127.0.0.1:8050');
        cy.wait(2000);

        // First, add at least one penguin to ensure the DB is not empty
        cy.get('#insert-demo-data-button').scrollIntoView().click();
        cy.wait(1000);

        // Verify there is at least one row in the table
        cy.get('#saved-penguins-table .dash-spreadsheet-inner tbody tr').should('have.length.at.least', 1);

        // Ensure the delete database button exists
        cy.get('#delete-database-button').should('exist').scrollIntoView();

        cy.on('window:confirm', () => true);
        cy.get('#delete-database-button').click();

        cy.wait(2000);

        // Verify the table is empty. A dash table without data might not have tr elements or will have a 'No data' placeholder
        // Alternatively, verify there are no data rows (tr with data-dash-row)
        cy.get('#saved-penguins-table .dash-spreadsheet-inner tbody tr td[data-dash-column="timestamp"]').should('not.exist');
    });
});
