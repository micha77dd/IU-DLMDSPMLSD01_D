describe('Manual Retraining of Models', () => {
    it('should retrain models when the retrain button is clicked', () => {
        cy.visit('http://127.0.0.1:8050');

        // Wait for websocket connection
        cy.wait(2000);

        // Ensure the retrain button exists
        cy.get('#retrain-button').should('exist');

        // Click the button
        cy.window().then((win) => { cy.stub(win, 'prompt').returns('admin123'); });
        cy.get('#retrain-button').click();

        // Check for the success message via websocket update
        cy.get('#ws-status-rf', {timeout: 15000}).should('contain.text', 'Random Forest: abgeschlossen');
        cy.get('#ws-status-svm', {timeout: 15000}).should('contain.text', 'SVM: abgeschlossen');
        cy.get('#ws-status-lr', {timeout: 15000}).should('contain.text', 'Logistic Regression: abgeschlossen');

        // Check that the last training time was updated
        cy.get('#last-training-time', {timeout: 5000}).should('not.contain.text', 'Noch nie');
    });
});
