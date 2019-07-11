'''
This is the leg class
'''

import maya.cmds as mc
import rigrepo.parts.arm as arm

class Leg(arm.Arm):
    '''
    '''
    def __init__(self, name, jointList, anchor='hip_swivel', dataObj=None, side='l'):
        '''
        This is the constructor.
        '''

        super(Leg, self).__init__(name, jointList, anchor, dataObj, side) 

        self.getAttributeByName("clavicleCtrl").setValue("pelvis_{}".format(side))
        self.getAttributeByName("swingCtrl").setValue("thighSwing_{}".format(side))


    def build(self):
        '''
        '''
        super(Leg, self).build()

        ikAnkleControl = self._ikControls[-2]
        ikGimbleControl = self._ikControls[-1]
        fkAnkleControl = self._fkControls[-2]
        fkGimbalControl = self._fkControls[-1]

        offsetJoint = mc.listRelatives(ikGimbleControl, c=True, type="joint")[0]
        fkOffsetJoint = mc.listRelatives(fkGimbalControl, c=True, type="joint")[0]
        mc.setAttr("{}.r".format(ikAnkleControl), 0,0,0)
        fkAnkleMatrix=mc.xform(fkAnkleControl,q=True, ws=True, matrix=True)
        mc.xform(offsetJoint, ws=True, matrix=fkAnkleMatrix)
        ikAnkleMatrix=mc.xform(ikAnkleControl,q=True, ws=True, matrix=True)
        mc.xform(fkOffsetJoint, ws=True, matrix=ikAnkleMatrix)