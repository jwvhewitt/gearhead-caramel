import exploration
import combat
import teams
import content
import ghdialogue



def start_mocha(pc):
    camp = content.narrative_convenience_function()
    if camp:
        camp.party = [pc,]
        camp.pc = pc
        camp.place_party()
        camp.name = 'Test'
        camp.play()



