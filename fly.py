from util import FlyCommand 

def fly_init():
    pass

def fly_execute(commond: FlyCommand ):
    print(commond)

    if commond == FlyCommand.NONE:
        pass
    elif commond == FlyCommand.TAKE_OFF:
        pass
    elif commond == FlyCommand.LAND:
        pass
    elif commond == FlyCommand.MOVE_RIGHT:
        pass
    elif commond == FlyCommand.MOVE_LEFT:
        pass
    elif commond == FlyCommand.MOVE_FORWARD:
        pass
    elif commond == FlyCommand.MOVE_BACKWARD:
        pass
    elif commond == FlyCommand.YOW_LEFT:
        pass
    elif commond == FlyCommand.YOW_RIGHT:
        pass
    
