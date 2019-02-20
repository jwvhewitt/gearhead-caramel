import exploration
import combat
import teams
import content
import ghdialogue
import configedit
import invoker
import cosplay
import gears
import chargen
import services



def start_mocha(pc):
    camp = content.narrative_convenience_function("SCENARIO_DEADZONEDRIFTER")
    if camp:
        mek = gears.Loader.load_design_file('Zerosaiko.txt')[0]
        mek.colors = gears.random_mecha_colors()
        mek.pilot = pc
        camp.party = [pc,mek]
        camp.pc = pc
        camp.place_party()
        camp.name = 'Test'
        camp.play()



