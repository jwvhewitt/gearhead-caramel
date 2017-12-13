import exploration
import combat
import teams
import content



def start_mocha(pc):
    camp = content.narrative_convenience_function()
    camp.party = [pc,]
    camp.place_party()
    camp.name = 'Test'
    camp.play()



