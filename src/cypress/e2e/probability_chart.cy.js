describe('Probability Chart dynamic species', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8050/');
    });

    it('shows custom species in probability chart', () => {
        const uniqueId = new Date().getTime();
        const customSpecies = `ChartPinguin-${uniqueId}`;

        // Add
        cy.get('#admin-species-input').type(customSpecies);
        cy.get('#admin-species-add').click();

        cy.get('#admin-species-feedback').should('contain.text', 'hinzugefügt');
        cy.wait(1000); // Give Plotly time to render the texts

        cy.get('#probability-chart').should($chart => {
            expect($chart.text()).to.contain(customSpecies);
        });

        // Delete
        cy.get('#admin-species-dropdown').type(`${customSpecies}{enter}`);
        cy.get('#admin-species-delete').click();

        cy.get('#admin-species-feedback').should('contain.text', 'gelöscht');
        cy.wait(1000); // Give Plotly time to render the texts

        cy.get('#probability-chart').should($chart => {
            expect($chart.text()).not.to.contain(customSpecies);
        });
    });
});
