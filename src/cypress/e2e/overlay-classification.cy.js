describe('Gespeicherte Klassifikation im Ergebnis-Diagramm überlagern', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8050')
        // Warten bis die Tabelle geladen ist (App ready)
        cy.get('#saved-penguins-table').should('exist')
        
        // Ensure there is at least one row of data by clicking insert demo data
        cy.get('#insert-demo-data-button').scrollIntoView().click()
        cy.wait(1000)

        // Und warten bis Daten da sind (seed daten)
        cy.get('#saved-penguins-table .dash-spreadsheet-inner table tbody tr').should('have.length.at.least', 1)
    })

    it('sollte keine Überlagerung anzeigen, wenn keine Zeile ausgewählt ist', () => {
        cy.get('#probability-chart .js-plotly-plot').should('exist')
        cy.get('#probability-chart').should('not.contain.text', 'Gespeicherte Klassifikation')
    })

    it('sollte die Klassifikation überlagern, wenn eine Zeile ausgewählt wird', () => {
        // Warten auf Event-Binding der Dash DataTable
        cy.wait(500)
        // Klicken auf eine reguläre Daten-Zelle anstatt force-click auf radio
        cy.get('#saved-penguins-table .dash-spreadsheet-inner tbody tr td[data-dash-column="timestamp"]').first().click()

        cy.get('#probability-chart').should('contain.text', 'Gespeicherte Klassifikation')
    })

    it('sollte die Überlagerung entfernen, wenn Eingabe zurückgesetzt wird', () => {
        // Warten auf Event-Binding der Dash DataTable
        cy.wait(500)
        // Klicken auf eine reguläre Daten-Zelle anstatt force-click auf radio
        cy.get('#saved-penguins-table .dash-spreadsheet-inner tbody tr td[data-dash-column="timestamp"]').first().click()

        cy.get('#probability-chart').should('contain.text', 'Gespeicherte Klassifikation')

        cy.get('#reset-button').click()

        cy.get('#probability-chart').should('not.contain.text', 'Gespeicherte Klassifikation')
    })
})
