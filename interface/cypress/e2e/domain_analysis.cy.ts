describe('Domain analysis flow', () => {
  it('limits growth triggers to three', () => {
    cy.intercept('POST', '/analyze', {
      statusCode: 200,
      body: {
        snapshot: {
          profile: { name: 'Acme Corp' },
          digitalScore: 75,
          vendors: [],
          growthTriggers: ['one', 'two', 'three', 'four'],
        },
      },
    }).as('analyze')

    cy.visit('/analysis')
    cy.wait('@analyze')
    cy.get('li[data-testid="growth-trigger"]').should('have.length.at.most', 3)
    cy.contains('Acme Corp')
  })
})
