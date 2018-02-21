from pbge import Singleton

# Environments

class GroundEnv( Singleton ):
	name = "Ground"

class UrbanEnv( Singleton ):
	name = "Urban"

class SpaceEnv( Singleton ):
	name = "Space"

class AquaticEnv( Singleton ):
	name = "Aquatic"

# Battlefield Roles

class Trooper( Singleton ):
	name = "Trooper"

class Commander( Singleton ):
	name = "Commander"

class Support( Singleton ):
	name = "Support"




