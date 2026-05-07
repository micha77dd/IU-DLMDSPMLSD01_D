describe('Disable on-demand training', () => {
    before(() => {
        // Delete all models using the UI button to ensure cross-platform compatibility (Windows/Linux)
        cy.visit('http://127.0.0.1:8050');
        cy.wait(2000);
        cy.on('window:confirm', () => true);
        cy.get('#delete-models-button').should('exist').scrollIntoView().click();
        cy.get('#last-training-time', {timeout: 5000}).should('contain.text', 'Noch nie');
    });

    it('should not train on-demand and should disable save button', () => {
        cy.visit('http://127.0.0.1:8050');

        // Check that warning is displayed
        cy.get('#prediction-summary').should('contain.text', 'Kein trainiertes Modell vorhanden');

        // Check that the save button is disabled
        cy.get('#save-prediction-button').should('be.disabled');

        // Manual classification should still work
        cy.get('#manual-classification-button').should('not.be.disabled');
        cy.get('#manual-classification-button').click();

        // Ensure the manual classification dialog is visible and works
        cy.get('h3').contains('Eigene Klassifikation').should('be.visible');

        // We don't save to keep DB clean, but the button should exist
        cy.get('#save-manual-classification').should('exist');
    });

    after(() => {
        // Retrain the models here so subsequent tests don't fail
        cy.visit('http://127.0.0.1:8050');
        cy.wait(2000); // Wait for websocket
        cy.window().then((win) => { cy.stub(win, 'prompt').returns('admin123'); });
        cy.get('#retrain-button').click();
        cy.get('#ws-status-rf', {timeout: 15000}).should('contain.text', 'abgeschlossen');
        cy.get('#ws-status-svm', {timeout: 15000}).should('contain.text', 'abgeschlossen');
        cy.get('#ws-status-lr', {timeout: 15000}).should('contain.text', 'abgeschlossen');
    });
});
