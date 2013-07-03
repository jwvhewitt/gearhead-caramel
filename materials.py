class Material( object ):
    def __init__( self , name , mass_scale , damage_scale , cost_scale ):
        self.name = name
        self.mass_scale = mass_scale
        self.damage_scale = damage_scale
        self.cost_scale = cost_scale


METAL   = Material( "Metal" , 5 , 5 , 10 )
MEAT    = Material( "Metal" , 5 , 4 ,  7 )
BIOTECH = Material( "Metal" , 5 , 6 , 15 )


