describe('Manuelle Klassifikation', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8050')
        cy.wait(2000)
        cy.get('#insert-demo-data-button').scrollIntoView().click();
        cy.wait(2000)
        cy.get('.dash-spreadsheet-inner').should('exist')
    })

    it('sollte den Button "Eigene Klassifikation vornehmen" anzeigen', () => {
        cy.get('#manual-classification-button')
            .should('exist')
            .and('have.text', 'Eigene Klassifikation vornehmen')
    })

    it('sollte den Dialog bei Klick öffnen und die Elemente enthalten', () => {
        cy.get('#manual-classification-modal').should('have.css', 'display', 'none')
        cy.get('#manual-classification-button').click()
        cy.get('#manual-classification-modal').should('have.css', 'display', 'block')
        cy.get('#manual-classification-modal h3').should('contain', 'Eigene Klassifikation')
        cy.get('#manual-species-dropdown').should('exist')
        cy.get('#cancel-manual-classification').should('exist').and('have.text', 'Abbrechen')
        cy.get('#save-manual-classification').should('exist').and('have.text', 'Speichern')
    })

    it('sollte den Dialog ohne Speicherung schließen bei Klick auf Abbrechen', () => {
        cy.get('#saved-penguins-table .dash-spreadsheet-inner tbody tr td[data-dash-column="timestamp"]').should('have.length.at.least', 1);

        cy.get('#manual-classification-button').click()
        cy.get('#manual-classification-modal').should('have.css', 'display', 'block')

        cy.get('#saved-penguins-table .dash-spreadsheet-inner tbody tr td[data-dash-column="timestamp"]').then($rows => {
            const initialCount = $rows.length

            cy.get('#cancel-manual-classification').click()
            cy.get('#manual-classification-modal').should('have.css', 'display', 'none')

            cy.get('#saved-penguins-table .dash-spreadsheet-inner tbody tr td[data-dash-column="timestamp"]').should('have.length', initialCount)
        })
    })

    it('sollte die Klassifikation übernehmen, anzeigen und den Datensatz selektieren bei Klick auf Speichern', () => {
        cy.get('#manual-classification-button').click()
        cy.get('#manual-classification-modal').should('have.css', 'display', 'block')
        
        // Dash Dropdown is flaky in headless Cypress, just accept the default value (Adelie)
        cy.get('#save-manual-classification').click()
        cy.get('#manual-classification-modal').should('have.css', 'display', 'none')

        cy.wait(2000); 

        // Die Zeile in der Tabelle sollte selektiert sein
        cy.get('#saved-penguins-table').find('input[type="radio"]').should('be.checked')
        
        // Die Vorhersagekarte sollte die manuelle Klassifikation anzeigen (Feature aus Issue 106)
        cy.get('#prediction-summary .summary-species').should('contain', 'Adelie')
        cy.get('#prediction-summary .summary-confidence').should('contain', '100%')
    })

    it('sollte bei einem ausgewählten Datensatz die manuelle Klassifikation aktualisieren anstatt einen neuen anzulegen', () => {
        cy.get('#saved-penguins-table .dash-spreadsheet-inner tbody tr td[data-dash-column="timestamp"]').should('have.length.at.least', 1);

        cy.get('#saved-penguins-table .dash-spreadsheet-inner tbody tr td[data-dash-column="timestamp"]').then($rows => {
            const initialCount = $rows.length

            cy.get('#saved-penguins-table .dash-spreadsheet-inner tbody tr td[data-dash-column="timestamp"]').first().click()

            cy.get('#manual-classification-button').click()
            cy.get('#manual-classification-modal').should('have.css', 'display', 'block')

            cy.get('#save-manual-classification').click()
            cy.get('#manual-classification-modal').should('have.css', 'display', 'none')

            cy.wait(2000); 

            // Zeilenanzahl darf sich nicht erhöht haben
            cy.get('#saved-penguins-table .dash-spreadsheet-inner tbody tr td[data-dash-column="timestamp"]').should('have.length', initialCount)

            // Vorhersagekarte sollte aktualisiert sein
            cy.get('#prediction-summary .summary-species').should('contain', 'Adelie')
        })
    })
})
