describe('Admin Metadata Management', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8050/');
    });

    it('does not display default species and islands in administration', () => {
        cy.get('#admin-species-dropdown').click();
        cy.get('body').then($body => {
            if ($body.find('.dash-dropdown-options').length > 0) {
                cy.get('.dash-dropdown-options').should('not.contain.text', 'Adelie');
                cy.get('.dash-dropdown-options').should('not.contain.text', 'Chinstrap');
                cy.get('.dash-dropdown-options').should('not.contain.text', 'Gentoo');
            }
        });
        cy.get('body').click(0, 0);

        cy.get('#admin-island-dropdown').click();
        cy.get('body').then($body => {
            if ($body.find('.dash-dropdown-options').length > 0) {
                cy.get('.dash-dropdown-options').should('not.contain.text', 'Biscoe');
                cy.get('.dash-dropdown-options').should('not.contain.text', 'Dream');
                cy.get('.dash-dropdown-options').should('not.contain.text', 'Torgersen');
            }
        });
        cy.get('body').click(0, 0);
    });

    it('allows creating, renaming and deleting a custom species', () => {
        const uniqueId = new Date().getTime();
        const customSpecies = `TestPinguin-${uniqueId}`;
        const renamedSpecies = `SuperTestPinguin-${uniqueId}`;

        // Add
        cy.get('#admin-species-input').type(customSpecies);
        cy.get('#admin-species-add').click();
        cy.get('#admin-species-feedback').should('contain.text', 'hinzugefügt');
        cy.get('#admin-species-feedback span').should('have.css', 'color', 'rgb(0, 128, 0)'); // green

        // Verify it exists in prediction dropdown
        cy.get('#manual-classification-button').click();
        cy.get('#manual-species-dropdown').type(`${customSpecies}{enter}`);
        cy.get('#cancel-manual-classification').click();

        // Rename
        cy.get('#admin-species-dropdown').type(`${customSpecies}{enter}`);
        cy.get('#admin-species-input').clear().type(renamedSpecies);
        cy.get('#admin-species-rename').click();
        cy.get('#admin-species-feedback').should('contain.text', 'umbenannt');
        cy.get('#admin-species-feedback span').should('have.css', 'color', 'rgb(0, 128, 0)');

        // Try renaming to empty (error)
        cy.get('#admin-species-input').clear();
        cy.get('#admin-species-rename').click();
        cy.get('#admin-species-feedback').should('contain.text', 'Fehler');
        cy.get('#admin-species-feedback span').should('have.css', 'color', 'rgb(255, 0, 0)'); // red

        // Delete
        cy.get('#admin-species-dropdown').type(`${renamedSpecies}{enter}`);
        cy.get('#admin-species-delete').click();
        cy.get('#admin-species-feedback').should('contain.text', 'gelöscht');
        cy.get('#admin-species-feedback span').should('have.css', 'color', 'rgb(0, 128, 0)');
    });

    it('allows creating, renaming and deleting a custom island', () => {
        const uniqueId = new Date().getTime();
        const customIsland = `TestInsel-${uniqueId}`;
        const renamedIsland = `SuperTestInsel-${uniqueId}`;

        // Add
        cy.get('#admin-island-input').type(customIsland);
        cy.get('#admin-island-add').click();
        cy.get('#admin-island-feedback').should('contain.text', 'hinzugefügt');
        cy.get('#admin-island-feedback span').should('have.css', 'color', 'rgb(0, 128, 0)');

        // Verify it exists in input dropdown
        cy.get('#island-dropdown').type(`${customIsland}{enter}`);

        // Rename
        cy.get('#admin-island-dropdown').type(`${customIsland}{enter}`);
        cy.get('#admin-island-input').clear().type(renamedIsland);
        cy.get('#admin-island-rename').click();
        cy.get('#admin-island-feedback').should('contain.text', 'umbenannt');
        cy.get('#admin-island-feedback span').should('have.css', 'color', 'rgb(0, 128, 0)');

        // Delete
        cy.get('#admin-island-dropdown').type(`${renamedIsland}{enter}`);
        cy.get('#admin-island-delete').click();
        cy.get('#admin-island-feedback').should('contain.text', 'gelöscht');
        cy.get('#admin-island-feedback span').should('have.css', 'color', 'rgb(0, 128, 0)');
    });
});
