describe('Delete models in Administration', () => {
    it('should delete all models when delete button is confirmed', () => {
        cy.visit('http://127.0.0.1:8050');
        cy.wait(2000);

        // Switch to administration tab if needed, but it's all on the same page in panels
        // Ensure the delete button exists
        cy.get('#delete-models-button').should('exist').scrollIntoView();

        // Intercept window.confirm is not needed for dcc.ConfirmDialog because it's a Dash component (wait, actually dcc.ConfirmDialog uses window.confirm in some versions or renders its own overlay. Wait, let's just click the button and handle it.
        // In Dash, dcc.ConfirmDialog uses window.confirm.

        cy.on('window:confirm', () => true);
        cy.get('#delete-models-button').click();

        // Check if the last training time updates to "Noch nie"
        cy.get('#last-training-time', {timeout: 5000}).should('contain.text', 'Noch nie');

        // Now verify the "Eigene Klassifikation" is the only thing we can do for the prediction save
        cy.get('#save-prediction-button').should('be.disabled');
    });

    after(() => {
        // Retrain the models here so subsequent tests don't fail
        cy.visit('http://127.0.0.1:8050');
        cy.wait(2000); // Wait for websocket
        cy.window().then((win) => { cy.stub(win, 'prompt').returns('admin123'); });
        cy.get('#retrain-button').click();
        cy.get('#ws-status-rf', {timeout: 15000}).should('contain.text', 'abgeschlossen');
    });
});
