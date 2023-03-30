import ceylon
from agents import source_agent

cy = ceylon.CeylonAI()

cy.register_agent(source_agent.source_agent)

if __name__ == '__main__':
    cy.run()
