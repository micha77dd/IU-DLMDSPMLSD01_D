describe('Dynamic Scatter Plot Axes', () => {
    it('should update the scatter plot axes when dropdowns change', () => {
        cy.visit('http://127.0.0.1:8050');

        cy.get('.tab').contains('Visualisierung').click();

        cy.get('#scatter-x-axis').should('exist');
        cy.get('#scatter-y-axis').should('exist');

        // Type and then click the option in Radix UI
        cy.get('#scatter-x-axis').click();
        cy.get('.dash-options-list-option').contains('Body Mass').click({force: true});

        cy.get('#comparison-scatter .g-xtitle').should('contain.text', 'Body Mass (g)');

        cy.get('#scatter-y-axis').click();
        cy.get('.dash-options-list-option').contains('Flipper Length').click({force: true});

        cy.get('#comparison-scatter .g-ytitle').should('contain.text', 'Flipper Length (mm)');
    });
});
