co = GameLogic.getCurrentController()

#get Scene
scene = GameLogic.getCurrentScene()

#get Objects
control_obj = co.getOwner()

obj = scene.getObjectList()


#get Sensors
sens = {}
sens['anim_next']   = co.sensors['anim_next']
sens['anim_prev']   = co.sensors['anim_prev']
sens['check_anim']  = co.sensors['check_anim']

#get Actuators
act = {}
act['anim']         = co.actuators['anim']

#get Properties
prop = {}
prop['state']       =  control_obj['state']
prop['frame']       =  control_obj['frame']
prop['direction']   =  control_obj['direction']

def set_prop(prop_name , prop_value) :
    control_obj[prop_name] = prop_value
    prop[prop_name] = control_obj[prop_name]






if sens['anim_next'].isPositive():
    #print "PLAY FORWARD %s" % (control_obj.name)
    set_prop('frame' , 1)
    set_prop('state' , 1)
    set_prop('direction' , 1)

if sens['anim_prev'].isPositive():
    #print "PLAY BACKWARD %s" % (control_obj.name)
    set_prop('frame' , 30)
    set_prop('state' , 1)
    set_prop('direction' , -1)

if sens['check_anim'].isPositive():

    parent = control_obj.getParent()
    if getattr(parent, 'state') == 1:
        set_prop('frame' , getattr(parent,'cur_frame') % 30 + 1)
#    if   prop['state'] == 0 :
#        set_prop('frame',1)
#
#    elif prop['state'] == 1 :
#        if prop['direction'] > 0 and  prop['frame'] < 30 :
#            set_prop('frame',prop['frame']+1)
#        elif prop['direction'] < 0 and  prop['frame'] > 1 :
#            set_prop('frame',prop['frame']-1)
#        else:
#            set_prop('state',0)
    
    GameLogic.addActiveActuator(act['anim'],True)
