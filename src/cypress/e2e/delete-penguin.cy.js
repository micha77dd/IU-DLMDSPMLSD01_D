describe('Delete record via trash icon', () => {
    it('should delete a record when clicking the trash icon', () => {
        cy.visit('http://127.0.0.1:8050');
        cy.wait(2000);
        // Insert demo data so we have something to delete
        cy.get('#insert-demo-data-button').scrollIntoView().click();
        cy.wait(2000);

        // Ensure the table is loaded
        cy.get('#saved-penguins-table').should('exist');

        // Wait for data rows to load (td elements)
        cy.get('#saved-penguins-table .dash-spreadsheet-inner tbody tr td[data-dash-column="timestamp"]').should('have.length.at.least', 1);

        // Get the initial number of data rows
        cy.get('#saved-penguins-table .dash-spreadsheet-inner tbody tr td[data-dash-column="timestamp"]').then(($cells) => {
            const initialCount = $cells.length;

            cy.wait(1000); // give dash table time to bind events
            // Click the delete cell. In dash table, the cell has data-dash-column, but might be within a specific row index.
            cy.get('.dash-cell[data-dash-column="delete"] .dash-cell-value').first().scrollIntoView().click();

            // Verify that the table now has one row less
            cy.get('#saved-penguins-table .dash-spreadsheet-inner tbody tr td[data-dash-column="timestamp"]')
                .should('have.length', initialCount - 1);
        });
    });
});