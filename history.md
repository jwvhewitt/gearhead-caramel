* Changed from multiple blocking 
* Improved map rendering speed; hopefully less choppiness
* Map positions clamped on display
* Animations are cached on game start

v0.977 May 4, 2025
* Added random artifact generator
* Added mystery missions
* Fire and smoke may result when terrain is damaged
* Attacks may cause damage to terrain
* Added AreaEnchantments
* Fixed bug with random MissionText
* Scenario builder automatically adds QOL reporter to cities
* Added message log

v0.976 April 10, 2025
* Fixed a bug in the containers unit
* Merit badges may have contra badges which get removed if badge earned
* Removed unusued and not working android import from pbge; if android support added later, will need to rewrite anyhow
* Added config troubleshooting option to disable scaling altogether
* Reworked screen scaling; can now manually set fullscreen resolution
* Fixed error causing jobless NPCs
* Faction based reaction modifier has been adjusted
* Fixed bug with conversation visualizer when NPC has reaction score of -100
* Rewrote name generator for hopefully more readable results
* Configured nuitka build, in case I ever need to change packager again
* Added ending to Raid on Pirate's Point
* Added relay plots
* Lancemate hire cost is at least $10,000
* Loading a dynamic plot now correctly sends an UPDATE trigger
* If changing team in world map war, player may become enemy of previous faction
* Fixed problems with factionless shops
* Fixed bug with text editor widget
* Added more quests to Raid on Pirate's Point
* Columns decor should not overwrite waypoint terrain
* Fixed bug with non-singleton city tags in bugs
* PC should now automatically reject most missions against favorable factions
* Automatic area invocations can be invoked with "accept" key or clicking icon
* Automatic area targeters no longer need to be targeted
* Fixed prev_invo invoker UI bug
* Added cruise movemode
* Fixed SimpleMonologueDisplay grammar error
* Destroyed sound fx now based on material
* Added slash anim for melee attacks
* Fixed bug with mecha being excluded from missions due to movement modes
* Added civilian ship megaprop
* Added Doom Buggy mecha

v0.975 November 29, 2024
* Updated the Allied Armor bookshelf
* Enchantments do not continue to update on dead/destroyed combatants
* Biotech mecha get a +2 action bonus
* Characters and mecha can spend stamina to get extra actions
* Added different cockpit control types
* Added High Output Engine, High Performance Engine
* Added Advanced Gyroscope; Gyroscopes are no longer Integral by default
* Fixed sound effect repeat bug
* Fixed dungeon branch naming bug
* A biotech torso can only install a biotech engine; non-biotech mecha may not use biotech engines
* Added Ravagers faction
* Biotech mecha can only mount biotech modules; non-biotech mecha may not mount biotech modules
* Reduced Stamina loss from cyberware
* Rebalanced monster dodge skill
* Corporate factions now have allies and enemies
* FieldHQ name buttons now use labels and can resize text if name is too long
* New MissionText generated if no MissionGrammar provided to BuildAMissionSeed
* Random MissionText added

v0.974 November 14, 2024
* Added "Road of No Return" quest to DeadZone Drifter
* Fixed unloadable save file if PC killed during combat bug
* Incapacitated PCs may need lifesaving cybersurgery
* FieldHQ contents are sorted now
* Scenes without a defined parent scene should get added as root scenes
* Most missions names now include faction being fought

v0.973 November 6, 2024
* Used cyberware is resold at a lower price
* Refactored cyberdoc unit to use current widget system
* Fixed crashing bug in cyberdoc unit
* AlertMenu will appear in front of widgets, like all other menus
* Fixed hover selection bug in WidgetMenu, ScrollColumnWidget
* Fixed crashing bug on Windows
* Sales menu will be properly reactivated after selling something

v0.972 November 3, 2024
* Fixed a bug in the Label widget

v0.971 November 3, 2024
* You can now access your inventory from the shop interface
* You can now switch characters in shop interface
* Added named boss monsters
* Room deploy method should not delete contents due to lack of space
* Can now reload guns and chemthrowers from the backpack interface
* Added SelectGearDataGatherer interface
* Guns and ChemThrowers have a reload option in combat if player has appropriate ammo in inventory
* Caption AnimObs may now have sound effects
* Invocations may now request additional data
* Can now purchase spare ammo clips and chem tanks in shops
* Refactored the shopping UI to use WidgetMenu
* Added WidgetMenu widget type
* Meat cannot be eaten in the middle of combat
* Added on_enter, on_leave properties for all widgets
* Fixed some errors in the [CHALLENGE] grammar tag
* Fixed blocking counter bug
* Fixed overlapping rooms bug
* Fixed some issues with Python 3.12
* Dialogue replies should more closely match context

v0.970 September 3, 2024
* Experience display in FieldHQ updated after training
* Increased Overwhelmed modifier from 3 to 4
* Altered NPC combat target selector 
* Fixed bug with pressing "Alt" key during combat
* Wall terrain types can be marked to not accept wall decor
* Added extra dialogue to Bear Bastard's Mecha Camp for Criminal PCs
* PlacableThing's altitude property now does something
* Combat can be set to keep going even if there are no active enemies on map
* Room contents with fixed positions will now be placed on map
* Props are immovable even after they are destroyed
* Props will not be placed somewhere they can block movement
* calc_mission_reward can automatically round the reward to a round number
* Former lancemates who show up in buildings where they've been before will not be indicated as current members of the lance.
* A captured territory must be consolidated before another territory can be invaded in WorldMapWar
* PCs dying in a city scene should now be handled properly
* ExpelFaction will now get rid of the town leader if the town leader is of the expelled faction
* Encounter plots will now clean up their own mess
* Random NPC generator reacts appropriately if faction=None passed as parameter
* Challenge plots can create a mission giver if one cannot be found
* Plots have new method to return a list of element candidates, allowing manual selection or sorting
* QuestOutcome involvement function replaced with player_can_fun
* More quest refactoring; verbs now objects, outcomes have elements

v0.962 April 5, 2024
* Fixed crash during Kerberos battle

v0.961 March 25, 2024
* Enemy teams can't attack a territory captured this turn in World Map War
* Commander will not retreat from Defeat Enemy Commander mission
* Fixed error with Raid on Pirate's Point unpickling
* Scenes now use a more robust method to make sure areas are traversable
* Fixed terrain indicator appearing under terrain border bug
* Added new eyecatch by Marjorie Gaber
* Fixed error in documentation of COMBATROUND trigger
* Combatant activation now handled by combat package

v0.960 February 11, 2024
* Fixed bug in DeadZone Drifter stub
* Certain weapons and mecha have been rebalanced; existing instances will be unaffected
* Weapon thrill power now _actually_ based on rank, ha ha ha
* Plots can contain extensions
* Added lore browser to memo system
* Refactored quest system to be entirely QuestLore based
* Okapi puzzle memo now uses same font (medium) as other memos
* Fixed world map encounters bug
* Burst fire weapons have increased thrill power
* Intercept weapons have their thrill power lowered
* Fixed do_partial_restore in MultiMission
* Closing doors via right click will now work
* Mouseover info will list items in tile
* Destroyed items appear red in inventory display
* All hidden models get revealed at the end of combat
* Window close button should now properly close the game
* Scenes and rooms will expand if larger area is needed for contents
* Weapon is_operational bug fixed
* Items on floor should always appear behind characters and mecha
* Lost forager will not be selected for random plots while lost
* Gradient map prep can now place rooms in requested bands

v0.957 September 25, 2023
* Fixed sound fx issues on certain platforms
* Game will no longer crash if campaign is ended between completing a mission and leaving mission, which is a situation that never occurs in any of the scenarios but if it ever did happen it would work now
* Fixed keys scrolling map when using a text widget

v0.956 September 18, 2023
* Added two new eyecatch cards by Radou
* Fixed AutoJoiner/AutoLeaver crash at world creation
* Plots may now modify cutscenes
* Added checkout sound fx to shop
* Some portrait bits tweaked by Anton Risberg
* Fixed crash if no boss monster generated for The Night Stalker plot
* Fixed numbers typo in DZD Wujung entry cutscene
* Fixed bug where campaign would remain in memory after quitting because of pbge.my_state.view

v0.955 September 13, 2023
* Fixed "deactivate_on_win" bug in older save files

v0.954 September 12, 2023
* Carrying capacity now shown for characters in backpack display
* Athletics skill now increases carrying capacity
* Right and left keys can be used to scroll through lancemates in inventory interface
* Increased damage of personal scale attacks
* Rebalanced some monsters to make them more dangerous
* Added config option to indicate lance members on map
* Fixed music volume bug
* Added some new portrait bits
* Fixed crash if PC name has space or special character in it

v0.953 September 5, 2023
* Fixed hacking prop bug

v0.952 September 5, 2023
* Added hacking invocations for Computers skill
* Fixed gender customization from character creator
* Added skill icon for "Listen to my Song"
* Changed the Scouting, Wildcraft abilities somewhat
* Added a help key for invocations interface, which defaults to F1
* Speaking to mecha should no longer cause a crash
* Objects in temporary scenes will never be chosen by seek_element
* Locked objects will never be chosen by seek_element
* All NPCs used in combat should now be locked

v0.951 August 24, 2023
* Fixed blue fog of war bug
* Fixed the "call_win_loss_funs_after_card" crash

v0.950 August 23, 2023
* Added the Scylla mecha from GH1
* TagBasedPartyReply will not display a major character's mnpcid
* Added ending scenes to DeadZone Drifter
* Can now use waypoints from the combat popup menu
* Added Onawa's quest to DeadZone Drifter
* Fixed duplicate grammar bug
* Updated Bear Bastard's Mecha Camp, Winter Mocha scenarios
* Added check_party_activation method to combat
* NPCs will give useful rumors first, then random chat
* Added pre-fx to conversation offers
* Single firing weapons can now cause critical hits, as in previous GearHead games
* Renown is now displayed for characters in the FieldHQ
* Added Quest procedural narrative generator
* Text formatter will now capitalize after "!" and "?"
* Team contents now stored as a ContainerList
* The get_scene method should return the correct scene even if called during adventure construction
* Okapi puzzle clue menus are now sorted
* There is a config option to turn off display of skill+stat in conversations
* Skill and tag based dialogue options will now show what skill+stat they're based on
* You can dock the tile info panel in the upper left corner via the config menu
* Combat clock troll bug fixed. Real ones will know.
* Enemy units get a different info panel border
* Mission objectives can now be reviewed from the memo browser
* The end-of-mission gate menu options have clearer wording
* Savegame validation should be much faster
* The map cursor changes to indicate enemy units + appropriate targets for abilities
* Label widgets can take a list of alternate smaller fonts to make text fit in specified area
* Added copy method to BuildAMissionSeed
* Challenges now deactivate on win by default
* Fixed error in list_nouns when two nouns provided
* Fixed text formatting error in WOTHCBM_HomeDespot plot
* Finished adding all of the mecha forms from previous games
* Renamed campaign property "day" to "time"

v0.946 December 15, 2022
* Fixed incorrect use of AutoOfferInvoker; added EffectCallPlusNPC
* Added procedural cutscene generator
* get_tags include_all now returns merit badge names and relationship info
* Fixed bug where lancemates removed to a safe place don't get removed
* Fixed a bug in the gear loader where everything is True, even False things are True
* Added Stream music mode
* Fixed bug when lancemate with pet quits party
* Fixed bug when reading black market sign with a pet in your party

v0.945 November 22, 2022, but slightly later in the afternoon
* Mecha scale monsters should never appear in human scale scenes, and vice versa
* Linked Fire/Multi Wielded weapons will only pay activation cost of primary weapon once
* Fixed bug in regroup at end of combat code
* Murder mysteries should get the victim's name right from now on

v0.944 November 22, 2022
* Key errors in dialogue processor will now show the dialogue that caused the problem
* You can no longer transfer inventory to pets or mecha owned by lancemates
* The images for saved games have their filename sanitized as well

v0.943 November 21, 2022
* Fixed crash when a lancemate uses a skill outside of combat
* Combat display now shows 99% as max chance to hit because of rounding error showing 100% for 99.5%

v0.942 November 20, 2022
* Added a clamp to prevent a rare and frankly inexplicable MemoryError exception in aibrain
* Fixed bug when pressing Esc key from stash/mecha parts selector
* Fixed bug with mecha inventory menu
* Fixed crash if campaign save file can't be found when the time comes to delete it
* Added preload_all_music configuration option
* Encourage can no longer be used on monsters (which caused it to crash)
* After combat, lance members will regroup so no-one is left in an inaccessible tile
* Campaigns now save the waypoint the current scene was entered from
* Fixed crash when sound player called while disable_audio_entirely is True 
* Disabling sounds in the configuration now actually disables sounds. Oops.
* Fixed lag in mecha exploration movement

v0.941 November 9, 2022
* Added filename sanitizer for user generated files; may not be perfect yet
* Fixed bug where style tags would not be applied to portrait bits later in list
* NPCs may eject if they are severely damaged and/or if they are intimidated by the PC's lance
* Increased the penalty for firing long range weapons at too short a distance
* Newly created mecha get added to the design list without needing to restart the game
* Fixed dialogue bug in DZREPC_CallOutChampionFight
* Lancemate development conversations should no longer have irrelevant convo options
* When gaining skill XP, your skill level can improve by multiple steps
* Fixed bug in GearHeadCampaign dole_xp method

v0.940 October 26, 2022
* Shop rank now calculated by item type
* Game will try to automatically switch to windowed mode if fullscreen causes it to crash
* The manual has been updated
* ~~Steam cloud saves should now be working~~ Steam cloud saves have been postponed until I find a Python wrapper for the Steam API that deals with them correctly
* Moved the user folder on Windows computers from Home to the app folder/ghcaramel_user

v0.932 October 19, 2022
* Added starting messages to Raid on Pirate's Point, and fixed bug in STARTING_PLOT component
* You can now set music volume, sound fx volume, and window size from config editor
* Changed configuration editor to a column widget rather than a menu
* Fixed bug where combat music won't start after resuming saved game
* Sound effect library preloaded at startup
* AnimObs now have support for sound effects
* Two audio channels are now reserved for music
* Added show_numbers_in_pilot_info config option

v0.931 October 13, 2022
* Added "Raid on Pirate's Point" scenario, early access version
* Fixed missing portrait/name when lancemate speaks during mecha combat
* Fixed bug in missions not counting retreat as a loss
* Changed the scene "END" trigger to "EXIT" to avoid conflict with the plot "END" trigger
* Added memos to the main quest of DeadZone Drifter
* Added "battle damage" to module display to aid color blind players
* Fixed music skip when entering/leaving buildings
* Fixed bug in Town Hall plot

v0.930 September 21 2022
* Working on new scenario "Raid on Pirate's Point"
* Fixed bug with SHOPS_PLUS INTERIOR_TAGS element
* Regular terrain sets now clear the surrounding area, including border
* Fixed bug with new FieldHQ modifications

v0.929 September 14 2022
* A lot of work has been done on the scenario editor (still only available in dev mode)
* Merit badges get their own tab in character display; show description and effects
* You can view a character's biography, if it exists, from the FieldHQ
* Fixed smudge on Trailblazer portrait
* You can set the default mission music for an entire campaign
* Added search path for music; may be located in player folder
* Fixed bugs in world map editor

v0.928 September 7 2022
* Added world map editor to scenario editor (still only available in dev mode)
* Added automatic tester for enemy conversation plots
* Fixed bug with Haywire and Poison status effects
* Added a lot more enemy character development conversations
* Added a new intro to DeadZone Drifter for Pop Star characters
* Music files are now cached, which should help avoid scene change disruptions

v0.927 August 29 2022
* Fixed bug in Cookies random plot

v0.926 August 29 2022
* Added many RANDOM_PLOT plots
* Search range dropped to 6
* The Neko is now properly a Gerwalk mecha
* Added Korean Name Generator class; not highly effective yet
* Changed the font family from "DejaVu" to "Source Han Sans" to provide Korean, Japanese, and Chinese support
* Faction reaction class can store faction leader
* pbge gets initialized before other units are imported

v0.925 August 22 2022
* Added image templates to the source code repository
* Added RestoreMP, RestoreSP effects
* Fixed bug when gear loader tries to load list inside a dict
* Added treasure types to monsters
* Monsters without legs don't get their movement rate downgraded
* Added tables and chairs to bars and coffee shops
* Campaign method get_relationship will return existing relationship if it exists
* Most dungeon encounters don't regenerate _every_ day
* Added dungeon extras to dungeon levels
* Added more signs for different businesses

v0.924 August 15 2022
* Fixed error in Kerberos dungeon
* Fixed error in Challenge.deactivate method

v0.923 August 15 2022
* Added Puma and Luna II mecha
* Most keyboard actions now use is_key_for_action method, may be changed in config.cfg
* Added a bunch more monsters
* Characters with Wildcraft >= 5 can call animal companions
* Added mouse_scroll_at_map_edges config option
* Fixed a bug in the PartlyUrbanGenerator
* WASD may now be used to scroll the map
* Default combat hotkeys changed to 1,2,3,4,5
* Refactored the map viewer to deal with tile-based focus and wrapping maps
* Pets will attempt to follow their trainer during exploration
* Added pets_can_die, directly_control_pets config options
* Changed restore to restore_all in Bear Bastard's Mecha Camp and Winter Mocha
* Text input widget now uses TextInput event
* Lancemates bring their pets with them when they join/leave the party
* Characters can have one pet

v0.922 August 13 2022
* Fixed a bug in one of the lancemate plots

v0.921 August 9 2022
* Added auto_center_map_cursor config option
* Combat hotkeys can't be used if the key has been assigned a system use

v0.920 August 8 2022
* AI will now jump as appropriate
* Changed jet types for mecha that previously have had flight or arc jets: Haiho, Phoenix, Trailblazer, Zerosaiko
* Jumping now works
* Added "Bear Bastard's Mecha Camp" tutorial
* Inventory can now be accessed from the exploration menu
* Characters and mecha get restored at the end of Winter Mocha. Oops.
* PCs stop hiding at the end of battle
* AdventureModuleData object now stores module's conversation border
* HALFMINUTE trigger generated every 30 seconds real time in exploration mode
* Shift + enter now has same effect as right mouse click in exploration mode
* Clumpy room now determines number of clumps by size of room
* Jobs can now have scene string tags as local requirements

v0.910 July 31 2022
* Ceramic now has a mass factor of 0.7
* Legs and wings give thrust bonus to movement systems mounted in them
* Added Wraith, Neko mecha
* Added option to always start at top of library when scrolling through combat actions
* Fixed bug with highway scene generator
* Widgets can now capture events, preventing other widgets from responding to same event
* Fixed bug with combat interface scrolling
* Mission will check environment, and warn PC if any lancemates cannot take part
* Added Androbot and Forgebot monsters
* Immobilized lancemates get left behind if their mecha cannot be repaired
* When placing gears on map, the environment is taken into account
* gear_up method now chooses appropriate move mode for the terrain
* Flying makes melee attacks more difficult for both parties
* Flying mecha get reduced cover modifier
* Multi-target invocations will now show a target counter beneath the invocation UI
* Added combat action clock
* Reworked the combat movement UI
* Fixed Ammo Explosion display bug
* Extreme speeds will now be slightly reduced
* Added Flight Jets, ARC Jets
* Added Aerofighter, Gerwalk mecha forms
* Random maps check blocked tiles using movemode provided by architecture
* Exploration movement uses movemode based on party's move modes
* Removed redundant code between MoveTo and BumpTo actions
* Config menu will delete config options that should not be in config.cfg

v0.905 July 23 2022
* Missing mecha descriptions provided by Baiby
* Configuration editor now validates configuration items
* Added BonusStrike attack attribute

v0.904 July 23 2022
* Added configuration option to announce start of player turn
* Fixed bug in configuration menu
* Added exception checking to gear loader
* Fixed bug in EditMecha when adding/removing Environments & Roles to new mecha
* Added AnimatedShotAnim
* Error message will be displayed if GHC crashes from main menu

v0.903 July 21 2022
* Fixed crash when trying to load corrupted egg file
* Fixed font bug when PC dies permanently
* Fixed bug with major NPCs sometimes not showing up
* Added Omega 1004 to DeadZone Drifter
* Fixed bug when game attempts to eject egg but PC has no mecha

v0.902 July 19 2022
* Added error logging for all game-crashing exceptions
* Fixed crash when player attempts to right-click use an inaccessible waypoint

v0.901 July 18 2022
* Scenario Editor city components pass METROSCENE even if not strictly necessary
* Changed pickle protocol from "latest" to "4" to preserve compatibility with SteamOS

v0.900 July 18 2022
* Fixed crash bug when PC killed
* Lancemates can repaint new mecha assigned to them; may be turned off via config
* Characters without assigned mecha colors get mecha colors when joining party
* Default window size may be set in configuration file
* PilotStatusBlock shows bars, not numbers, for HP, MP, SP
* Added BeingStatusBlock for characters and monsters
* You can go straight to inventory by pressing "i"
* Edit Scenario has been moved to Dev Mode only due to the fact that it needs some work
* Containers now visibly open when you open them, so you can see what you've already looted
* Mechanical Tarot has been completely replaced with Challenge/Resource system
* Fixed a rare pathfinding in combat bug
* Fixed a rare infinite recursion bug in end_plot
* You can now say goodbye from an info offer
* Added LOCAL_PROBLEM plots to replace the old Mechanical Tarot
* Left mouse click will now escape from memo browser
* equip_combatant will now upgrade equipment as appropriate if an NPC has already been equipped
* faction_list from design files now gets error checked
* Building TerrSets now record their footprint
* Personal scale armor will now show armor rating and damage
* Warning shown if campaign save file is from an earlier major version
* Load game menu now shows character portrait and adventure thumbnail
* Character egg files will not be deleted if adventure selection cancelled
* Unloadable campaign files will be placed in quarantine
* Added more options to the in-game configuration editor
* Changed the Campaign save file specification
* Maximum XP from destroying a target reduced to 100
* Replaced manually constructed rumors with Rumor objects
* Rumors may now have an effect for their info offer
* Merged dd_lancedev.py into lancedev.py
* Added some new Lancemate personality types
* Villages in DeadZone Drifter get custom colors
* Fixed bug when selecting "None" after previously selecting clue in okapi puzzle widget

v0.830 June 21 2022
* Added "Skippy's Night Out" mystery to Wujung in DeadZone Drifter
* GH1 import now includes all NPCs that have a relationship with the PC
* Gears can now be marked as stolen; only certain shops will buy those
* GearHead Campaign now has method for loading major NPCs
* Memo browser is now a widget, and memos can create custom widgets
* Terrset now actually draws border
* Added new eyecatch screen by Sierra Bravo
* Fixed the map scrolling problem at the edges and corners of the map
* Fixed a longstanding bug with Architecture.draw_fuzzy_ground
* Added PartlyUrban map generator
* Random map room placement should now be more robust
* Floor borders now based on priority, not keyed to specific terrain pairs
* Changed the way custom factions are stored and accessed in Scenario Creator
* Scenario editor now does basic error checking before compiling
* Focus mode added to scenario editor physical view
* Added identifier, literal scenario creator variable types
* Justify property now works with text entry and text editor widgets
* ScenarioCreator output is pretty printed with yapf if available
* Refactored the ScenarioCreator compiler
* Text editor widget now a column of text entry widgets; cursor movement works properly
* Text entry widget now has movable cursor
* Scenario Creator has subplot loader utility which passes all element aliases
* Scenario Creator builds the world before loading subplots
* Possibly fixed the problem with pygame.quit() not really quitting
* Scenario creator variables return their own widgets; may return a list of widgets rather than a single widget
* Elements defined by BluePrints get their own unique ID
* PlotEditor renamed to ScenarioCreator
* Scenario variable types all have their own classes now
* The map focus cannot leave the bounds of the map

v0.821 March 31 2022
* Fixed the loverboy beard error
* ScrollColumn widgets may force focus
* ScrollColumn widgets act like menus when accessed by keyboard
* Widgets may provide their own keyboard handling
* Added mapcursor module; can be used to move & target invocations via the keyboard
* Holding shift with tab will select the previous widget

v0.820 March 13 2022
* Added the Ice Wind mecha family
* Added more portrait bits
* Update trigger automatically updates plots
* Trigger check during campaign construction will no longer cause crash
* Left and right keys may be used to browse memos
* Campaign now has get_memos method
* Challenges can have memos integrated into them
* Fixed so many bugs. How many bugs? Lost track. Lots and lots of bugs.
* Active Challenges are listed in GHNarrativeRequest
* Added Challenges and Resources
* Right clicking on combat radio button will bring up library menu
* Widgets may now be given an "on_right_click" property
* Radio buttons widget now takes dicts to describe the button properties
* Fixed portrait placement bug with lancemate menu item
* Phasing out IgniteAmmo attribute; to be replaced by BurnAttack attribute
* Ammo may now explode if destroyed
* Destruction of important parts will be displayed
* Added Antidote usable item and Cure Poison ability for Medicine skill
* Added Agonize, PoisonAttack attack attributes

v0.810 November 30 2021
* Gears may have individual campdata dicts which don't get exported when campaign is finished
* Noncombatants flee from combat
* Added "FAINT" trigger
* Fixed bug in which GearHeadCampaign all_plots method did not return metro plots
* Added automatic update and expiration for plots
* Added automatic rumor/info offer/memo option for plots
* You can now edit your PC's name, portrait, and gender from the FieldHQ
* Gender is now completely customizable

v0.800 September 30 2021
* Campaign save file compatibility probably broken; character save files are okay
* PlotCreator blueprints now automatically sorted
* You can start a newly compiled scenario without restarting the game
* PlotCreator updated to use campfeatures utilities
* MissionBuilder no longer needs environment parameter, since this info is included in GearHeadArchitecture subclass
* Added some hand-painted portrait bits
* Added ArenaRules scene attribute
* Character tags include the tags of that character's faction
* Lancemates will not rejoin the party if they currently dislike the PC
* Lancemate reaction score will decrease if that lancemate is incapacitated or loses their mecha
* Unfavorable NPCs limit their conversation options
* Added standardized in-town recovery/lance development loader
* Added militia defense if PC attempts to enter an unfavorable town
* Added standardized world map encounter handler
* The Terran Defense Force mission in Wujung can now be rejected, and stops being offered after 20 wins
* Fighting a mission against a faction may make that faction unfavorable to the PC
* Added is_favorable_to_pc, is_unfavorable_to_pc methods to GearHeadCampaign
* Added Campaign go method
* Singletons should return the intended str() value

v0.700 June 13 2021
* Added PlotCreator scenario editor
* Popup menu can now take custom width and height
* Colors have been added to the SINGLETON_REVERSE dict
* Fixed problems with choose lifepath display
* The map viewer now uses a per-tile message ticker
* Added "View Hotkeys" to combat popup menu
* DZD roadedge plots will stop rumors after the road is cleared
* Added "center on party" to exploration menu
* Fixed crash when prop goes haywire
* Increased threat value of hunter synths

v0.620 April 9 2021
* Added pilot suit portrait bits by LordErin
* Added some more opening scenarios
* Fixed bug when running ghcaramel from a different directory
* Combat hotkeys can be set by pressing Alt + Key when using desired action, or by editing config file
* Combat popup menu added if right mouse button clicked
* Alert will now return the event that ended the alert display
* MissionBuilder mission now checks scene environment for legal mecha
* Added a local feature to each village in DeadZone Drifter
* Increased size of standard dungeon level to 65x65
* SceneConnectors now take narrative request as first parameter
* Fixed fullscreen lockup on Linux
* Added DuckTerrain, duck_dict option for TerrainSet
* Robot NPCs from GH1 will be Metal, not Meat
* Lancemates from previous adventures may show up in DeadZone Drifter

v0.612 January 13 2021
* Added the CNA-15 Century mecha
* Fixed bug with importing GH1 characters

v0.611 January 4 2021
* Added a description to the DeadZone Drifter adventure module
* Updated the README.md file for the first time in ages
* Packaging system changed from PyInstaller to cx_Freeze, fixed Windows NumPy issue
* Added Adventure Module selection menu
* Moved faction score from a Character property to an Egg property
* Color menu will recognize identical colors now
* Reworked the way scatter damage scatters
* Added Eggzaminer to dev mode
* Fixed Egg ejection bug
* Fixed a lot of GH1 import bugs
* Fixed a problem with asynchronous IO and menus
* Lancemates and major NPCs should be imported correctly from GH1
* Cybertech skill imported correctly from GH1
* Vadel's hover jets are now bigger and integral
* Zerosaiko mass driver improved
* Changed the formula for armor damage absorption
* Reduced chemthrower chem usage
* Scene viewer may now get postfx function called after normal map rendering
* Fixed bug with LancematePrep cutscene element
* PC can bring mecha, stash with them between adventures
* Updated the Winter Mocha scenario
* Python scripts in user content folder will be loaded at startup

v0.600 December 27 2020
* DeadZone Drifter scenario now has a conclusion
* Monsters may get a different number of actions per round
* Fixed serious CharacterMover bug
* Mecha scale beings have their Mobility calculated correctly
* Burst fire bonus applied to accuracy, not to hit roll
* XP for destroying enemy is capped at 500
* Added skill trainers
* CharacterMover will not move NPC back to original scene if NPC gets moved away from dest scene to another scene first
* Haywire now correctly works on human-scale robots
* Added consumable items
* Added more cyberware from GH1, GH2
* Combatants who are out of visual range and don't know where to go next will deactivate
* Lancemates moved by CharacterMover will be removed from party and re-added if possible at end of plot
* Potential lancemates can tell you a little bit about their skills
* Most random lancemates will start with lower renown, but may have extra skills
* Added merit badges for GH1 PCs who defeated Cetus, Ladon
* Shops without a defined faction will use the faction of the town they're in

v0.560 November 29 2020
* Added Kerberos storyline to DeadZone Drifter
* Can now load same image in transparent and non-transparent versions
* Monsters can power their own weapons
* Can now flee from combat by using an exit
* Attackers will move a bit so you can tell who's attacking
* Added AttackInvocation
* Added COMBATROUND script trigger
* Added error message to gear loader if unknown command encountered
* Activated the BioCorp biotech hunting mission
* Added missing formatting for many tarot memos
* Nerf Charge Attack, which was incorrectly not rescaled during the previous health and damage scale adjustment in 0.542.

v0.551 October 20 2020
* Added auto_save default to data/config_defaults.cfg
* Reduced Corsair's heavy rocket pod to 4 rockets, but bigger ones

v0.550 October 15 2020
* Added Ran Magnus Mecha Works
* Added stretchy_screen config file option
* Added Pro Duelist Association faction
* Missile salvos drain target's stamina faster than other attacks
* Removed redundant (and outdated) are_ally_factions, are_enemy_factions methods from GearHeadCampaign
* Improve success rate and casting cost of LISTEN TO MY SONG.
* Fill out Mecha Graveyard adventure.
* Highlight the tile where we completely consume one action point when showing the trail of a move or move-attack.
* Fix the missing Haywire attack on Phoenix L-Cannon
* Added unique EWar system, Necromatix. Start doing those sidequests for a chance to get it!
* Fix bug that would prevent deadzone town plot from advancing if you do "Recon by Force" mission.
* Fix bug where we mistakenly give odds for hitting a dead mecha when its ally is standing on top of it.
* Some particular unique shops might now sell parts of, or even complete, champion mecha.
* Fix bug where mechas you own suddenly disappear after you take out their engines or torso in the mecha engineering terminal.
* More body options.
* Implement 'Create New Mecha' in out-of-game mecha editor.
* Add batteries to Musketeer.
* Champions that upgrade their missiles now make sure it fits in the largest Launcher.
* Memos now include location information as appropriate.
* Made missiles more accurate, cheaper, and not shield-blockable (now only interception and dodge work against missiles), and increase missile quantities on almost every mecha.
* Intercept weapons are now much less effective, but you can now stack several to improve your interception chances.
* Added some dungeon decor
* Destroyed mecha will be announced at end of combat
* Slightly increased and curved damage
* Missions change your faction score for both enemy and allied factions
* Only one LMDEV plot can be active at once
* Added GET trigger when an item is picked up

v0.542 August 18 2020
* Added Mecha Graveyard adventure
* Adjusted mass, health, and damage scaling
* Added crates and other item-storage waypoints
* Mecha melee damage bonus also toned down
* Melee attack multiple hits toned down
* Added Treasure gear type
* Dropped items may be picked up by clicking on tile where PC is standing
* Lancemates may now trade personal inventory items
* Monsters use a different target selection routine
* Got rid of annoying short hallways from PackedBuilding map generator
* Melee weapons can have the Multi Wielded attribute, which lets you attack with multiple instances of that weapon.
* Personal scale combat gives more direct XP than mecha scale combat
* Added dungeon generator
* Random NPCs should get a faction-appropriate job
* Standardized the lancemate hiring cost
* Tooltips may be several lines of text, if needed

v0.541 August 10 2020
* Added Phoenix and Secutor mecha
* Modified some mecha designs
* Added Brutal attack attribute that causes extra damage to armor
* Melee attacks have a chance to cause multiple hits
* Fixed autosave config menu option
* Melee weapons can have the Ignites Ammo attributes, which replaces Burn for melee weapons, and reduces armor of enemy mecha, preventing them from using ballistic and missile weapons.
* Melee weapons can have the Drains Power attribute, which greatly reduces the power supplies of enemy mecha, preventing them from using energy and beam weapons.
* Heavy actuators provide melee damage bonus to the module they're installed in
* Melee attacks now get a damage bonus
* Attacking a model will activate it
* When combat starts, all nearby teams are activated
* Added advanced EW programs
* Added the Solar Navy faction
* Vikki now gives a brief tutorial about mecha and pilot stats
* Combat AI for enemies updated; target choice is no longer random or permanent
* Random NPCs should now have consistent mecha colors
* Tarot cards marked as UNIQUE should now be unique (unless generated during play)
* Enemy factions in missions may bring in allies iff all faction members are busy
* DZD town threat rank increases as you move deeper into the dead zone
* Fixed FactionComputer password bug

v0.540 July 31 2020
* All towns now have a tarot scenario
* Added Quality of Life indicator to all towns
* Highway encounters won't clutter the road with trees or other obstacles. It's supposed to be a road.
* Fixed the disappearing enemy commander bug
* One on One Champion Fight now uses faction leader if possible
* Town prosperity now affects shop items
* Larger movement systems are now lighter (two size-3 Wheels is heavier than a size-6 Wheels) but more expensive.
* Slasher champions upgrade their plain shields to beam shields.
* Raider champions upgrade their sensors (to take advantage of their weapon increased range) and may also gain Overchargers.
* Tone down EnergyWeapon prices.
* Add Explodium champion. Boom!
* Major NPCs now always get customized mecha
* Dungeons will clean out their dead daily
* Combatant NPCs get starting equipment
* Added Monster gear type
* Improved visibility of Green Boarding Chute
* Added storage scene to GearHeadCampaign
* Tarot card transformation now passes on default elements from alpha card.
* Add Overchargers.
* Champion mecha are special, so they should be easier to salvage.
* Increase Charge cost even more: treat it like a ranged weapon.
* Added Daum, Vadel mecha
* Melee weapons blocked by energy weapons or beam shields take damage
* Added beam shields
* Added indie plots
* Renamed the tarot card modules
* More variety in road stop garages.
* In combat, default to the fastest movemode of your mecha.

v0.530 June 8 2020
* Revamped shop interface
* Style rules may be turned on or off in the portrait editor
* Added style, nostyle properties to PortraitBits
* Adjusted mecha cost, random mecha unit generation
* Modified the volume of missiles
* Added Razer, Petrach, Wolfram mecha
* Character creator allows selection of local mecha for green zone, dead zone
* Extremely high Mobility scores toned down
* Fixed crash when pygame.mixer fails to load
* Fixed some mission problems
* Added Memory records to Relationships
* Random NPCs start with a narrower range of stat points

v0.520 May 16 2020
* Mechanical Tarot scenario generator improved and expanded
* Can't enter a mecha combat mission if you have no mecha
* No reason for Gyroscopes to not be integral by default, so now they are integral by default
* Fixed lake room map generator crash
* You can no longer install characters into mecha cockpits, which can lead to broken savefiles.
* You might now occassionally come across specially-named mecha on some mission objectives. If you're lucky you might even salvage them and their special modified equipment.
* Party removed to a safe location when plot controlling temporary scene ends
* Added longform mecha info panel
* Invocations now consistently show their casting costs.
* Can now remove all modules from a mecha without crashing the game.
* Show more info on items in Field HQ and Shop.
* Improved Haiho slightly.
* More movement systems for sale.
* Cyberware!
* Argh. Maybe now wall decor will stop blocking doors?
* Fixed json files not loading in Python 3.7+

v0.511 May 1 2020
* May scroll up/down or use up/down keys to page through all combat modes
* EWSystems now show their programs, Engines now show their ratings in their info panels when buying or choosing parts to install
* Added SkillBasedPartyReply and TagBasedPartyReply
* Add Take Cover action to Stealth and Spot Behind Cover to Scouting
* Spot Weakness is now a Science skill
* Negotiation now lets you recover lancemate Mental by spending your own Stamina
* Performance now gives weaponized singing in combat.  LISTEN TO MY SONG
* SensorLock negates the SensorRange attack modifier
* Added StatValuePrice effect price
* GearHeadCampaign now has make_skill_roll method
* Added extra cost factor for high Accuracy, Penetration weapons
* Increased Charge cost modifier to 2.5
* Hopefully prevented rooms from being completely blocked off
* Add an AI Assistant program, and a C99 AI Assistant EW System
* Fixed a bug in lance "friendly duel" challenge
* Armor, Sensors, Wheels, Hover Jets, Heavy Actuators now show their size, material, and integral-ness in their displayed name
* Enchantments can now modify to-hit based on cover
* Enchantments can be dispelled by application of other enchantments
* Added Wujung Tires
* Solitary walls will be correctly displayed
* Wall decor should not be placed on same tile as a door
* Added Musketeer, Ultari, Haiho mecha
* Mecha missions now feature a variety of room types
* Enchantments can be dispelled on movement
* Added tidy_enchantments method to GearHeadScene
* Added LinkedFire attack attribute
* Many non-weapon gears can now be integral (which makes them non-removable in-game, but gives volume reduction and possible cost and mass reduction).
* Integral weapons can no longer be removed in-game, and are also shown as integral.
* Field of view will be updated after charge attacks
* Cannot give stash items to mecha that don't belong to you

v0.510 April 19 2020
* Range attack modifier will now display "Too Far" or "Too Close"
* Gauss Cannons now use Perception rather than Reflexes
* Added HostilityStatusBlock
* Fixed ORPH_SOCIABLE lifepath node
* Added Kojedo mecha
* No experience award for missions you don't even attempt
* Owner indicated for all items in FHQ
* Cannot access inventory of mecha that don't belong to you
* Fixed crash from TargetIsDamaged AI targeter
* Added disable_audio_entirely troubleshooting config option
* Game still loads if audio device fails
* Fixed recovery plot when lancemate dies
* Fixed weird PFOV bug (at least one, hopefully two)
* Repaired the Repair skill
* Fixed crash from targeting with Flail weapons
* Exhaustion happens sooner in combat, has bigger penalties
* Adjusted renown rewards
* Fixed random NPCs always combatants bug
* Changed "Dominate Animal" skill to "Wildcraft"

v0.500 April 12 2020
* Reduced weapon volume
* Added mecha editor, mecha browser
* Added Haywire, Overload attack attributes
* Effects, combat now grant experience, skill experience
* Switched to Python3
* Added restore method which refreshes gears, returns repair/reload cost (gears/base.py)
* Immobility modifier separated from speed modifier (gears/geffects.py)
* Added reflexive pronoun to gender
* Randmaps plasma now scales to be close to map size
* Reworked the menu unit for better mouse support
* Conversation border is now set by campaign
* You can now ask lancemates to leave the party
* Added road map to DeadZone Drifter
* Fixed bug with Alert, AlertDisplay locking
* NPCs move during exploration
* Added dev_mode_on config option (main.py)
* Fixed bug with random NPCs getting wrong job skills (gears/selector.py)
* Added training interface (game/fieldhq/training.py)
* Moved all plot-defining units to game/content/ghplots
* Pilot attacks no longer included in mecha attack list (gears/base.py)
* Invocations UI now responds to mousewheel scroll, key commands (game/invoker.py)
* Attack UI will remember the last weapon used (game/combat)
* Changed local_teams to regular dict (pbge/scenes)
* Fixed recursion problem with deepcopy (gears/base.py)
* Added ammo count to attack widget (game/combat/targetingui.py)
* Fixed crash when using color menu with PyGame 1.92+ (game/cosplay.py)
* Incorporated caramelcolor extension module (pbge/image.py)
* Scale, material passed as defaults to children by text gear loader (gears/__init__.py)
* Widgets only respond to clicks if first widget this tick (pbge/widgets.py)
* Added fieldHQ and backpack (game/)
* Added character generator (game/chargen)
* Added services (game/services.py)
* Currently visible area indicated (pbge/scenes/viewer.py)
* NPC relationship with PC now tracked by Relationship object (gears/relationships.py)
* Added merit badges (gears/meritbadges.py)
* Added jobs system (gears/jobs.py)
* Can activate waypoints via the popup menu (game/exploration.py)
* Random mecha units get random team color if no faction (gears/selector.py)
* Standardized GearHead architectures (game/content/gharchitecture.py)
* Added cosplay module (game/cosplay.py)
* Portrait generator now used by VisibleGear class (gears/base.py)
* Gender may be defined as dict in design files (gears/base.py)
* Added gender (gears/gender.py)
* Player folder now has an image subfolder (gears/)
* Images now have a search path (pbge/image.py)
* Mechanical Tarot can generate causality chains (gears/mechtarot.py)
* Added portraits module (gears/portraits.py)
* Added tarot to GearHeadCampaign (gears/)
* HeightfieldPrep can set maximum levels of lowground, highground (pbge/randmaps/prep.py)

v0.130  June 17, 2018
* Added Joust, Trailblazer mecha
* Added charge attacks (gears/geffects.py)
* Added BurnAttack status effect (gears/attackattributes.py)
* Repair will remove appropriate enchantments (gears/geffects.py)
* Added enchantments
* NPCs will use skills in combat as appropriate (game/combat/aibrain.py)
* Added Search invocation (gears/stats)
* Added Stealth invocation (gears/stats)
* Centralized the move-then-invoke code (game/combat)
* Default offers automatically added to conversation (pbge/dialogue)
* VisibleGears have a shadow (gears/base.py)
* PlaceableThings may be hidden (pbge/scenes)
* Exploration right click menu now works properly (game/exploration.py)
* Combat skill button only shows up if PC has usable skills (game/combat)

v0.120  March 9, 2018
* Version indicated on title screen (main.py)
* Repair skills working (gears/stats.py)
* Added skill invocations (gears/stats.py)
* Added generic invocation targeting UI (game/invoker.py)
* Head mounted sensors get a range bonus (gears/base.py)
* Added ChemThrower, Chem gears (gears/base.py)
* Ammo cost, mass, volume now affected by attributes (gears/base.py)
* Added names_above_heads config option (pbge/scenes/viewer.py)
* Added option to disable music (pbge/)
* The Esc key will now bring up an options menu in-game (game/)
* Added configuration editor (game/configedit.py)
* Reduced power cost of energy, beam weapons (gears/base.py)
* Added Intercept, Flail, Defender, ConeAttack, LineAttack
  attack attributes (gears/attackattributes.py)
* Added Parry, Intercept defenses (gears/)
* Successfully blocking with shield damages shield, costs 1 stamina (gears/)
* Attack invocations record "thrill power" (gears/geffects.py)
* Modules now have attacks (gears/base.py)
* Shields cause aim penalty for weapons in same arm (gears/base.py)
* Head mounted cockpits provide +10 Mobility (gears/base.py)
* Fixed crash when player mecha runs out of attacks (game/combat)
* Added random mecha selector (gears/selector.py)
* Improved the enemy AI (game/combat/aibrain.py)

v0.111  February 15, 2018
* Fixed a dialogue bug in one of the mocha encounters
* Random pilots get random personalities (gears/__init__.py)

v0.110  February 14, 2018
* Enabled loading screens (pbge)
* Added Props (gears/base.py)
* PC should always count as lead party member (game/exploration.py)
* Rewrote dialogue generator to dynamically create each exchange (pbge/dialogue)
* Added cutscenes (pbge/cutscene.py)
* Rooms may be saved for use by scripts (gears/__init__.py)
* Fixed place_party bug (gears/__init__.py)
* Centralized the start_conversation code (game/ghdialogue)
* Fixed free_pilots bug (gears/base.py)
* Movement into range indicated in targeting UI (game/combat/targetingui.py)
* Centralized info display code (gears)
* Added Scatter damage type (game/geffects.py)
* Clicking enemy opens attack menu (game/combat/movementui.py)
* Music is preloaded when scene entered (pbge,game/exploration.py)
* Added OddsInfo block (gears/info.py)
* Melee, Energy attacks ignore target speed (gears/base.py)
* Added Mental, Stamina, and Power (gears/base.py)
* Blast attacks cannot be dodged (gears/geffects.py)
* Energy weapons cut through armor like a hot knife (gears/base.py)
* Added Accurate, BurstFire, Blast attack attributes (gears/attackattributes.py)
* Named waypoints indicated on mouseover (game/exploration.py)
* Border transparency now uses same alpha as GearHead1 (pbge)
* Combat starts when PC moves within half sensor range (game/exploration.py)
* Targeting info shows top three modifiers (game/combat/targetingui.py)
* "card_" portraits contain sprite (game/ghdialogue/gdview.py)
* Images may now have custom frames (pbge/image.py)
* Fixed bugs with Overwhelmed, Target Movement modifiers (gears/geffects.py)
* The InfoPanel is now modular (gears/info.py)
* Added Plot.activate, Plot.deactivate methods (pbge/plots.py)
* Fixed party walking order during exploration bug (game/exploration.py)
* Fixed move-then-fire bug (game/combat/targetingui.py)

v0.100  December 23, 2017
* First public release
