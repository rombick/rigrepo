'''
This is a module for libraries used for transforms.
'''
import maya.api.OpenMaya as om
import maya.cmds as mc
import maya.mel as mm
import rigrepo.libs.common as common

def addPoseInterp(name, driver=None, createNeutralPose=0, twistAxis=0):
    '''

    :param name: Name of interpolator node
    :param driver: driver name
    :param createNeutralPose: Add swing, twist, and swing/twist neutral pose
    :param twistAxis:
    :return: poseInterpolator
    '''

    if driver:
        mc.select(driver)
    poseInterp = mm.eval('createPoseInterpolatorNode("{}", "{}", "{}")'.format(name, createNeutralPose, twistAxis))
    return poseInterp

def getPoseInterp(node):
    node = common.getFirstIndex(node)
    if mc.nodeType(node) == 'transform':
        shape = common.getFirstIndex(mc.listRelatives(node, s=1, ni=1))
        if shape:
            node = shape

    if mc.nodeType(node) == 'poseInterpolator':
        return(node)

def renamePose(poseInterp, poseName, newName):
    '''

    :param poseInterp: Pose interpolator transform
    :param poseName: Name of pose
    :param newName: New name of pose
    :return: None
    '''
    # api call
    #mm.eval('poseInterpolator -edit -rename {poseName} {newName} {tpl};'.format(tpl=tpl,
    #                                                                            poseName=poseName,
    #                                                                            newName='shoulder_l_down'))
    mm.eval('poseInterpolatorRenamePose {poseInterp} {poseName} {newName}'.format(poseInterp=poseInterp,
                                                                           poseName=poseName,
                                                                           newName=newName))
def addPoseControl(poseInterp, controlAttr):
    '''
    Adds anim control as a pose controller (driver controller). When going to a pose this sets up
    what values are set on the driver controllers.

    :param poseInterp: Pose interpolator transform
    :param controlAttr: Anim control and attribute to add to the pose controls for the pose interpolator.
                        Example: shoulder_fk_l.r
    :return: None
    '''

    poseInterp = getPoseInterp(poseInterp)
    poseInterpAttr = poseInterp + '.driver[0].driverController'
    index = mm.eval('getNextFreeMultiIndex("{poseInterpAttr}", 1)'.format(poseInterpAttr=poseInterpAttr))
    mm.eval('connectAttr -f "{controlAttr}" "{poseInterpAttr}[{index}]" '.format(controlAttr=controlAttr,
                                                                                 poseInterpAttr=poseInterpAttr,
                                                                                 index=index))
def removePoseControl(poseInterp, controlAttr):
    controlAttr = common.getFirstIndex(controlAttr)
    poseInterp = getPoseInterp(poseInterp)
    poseInterpAttrs = mc.ls(poseInterp + '.driver[0].driverController[*]')
    control = controlAttr.split('.')[0]
    for attr in poseInterpAttrs:
        conControl = common.getFirstIndex(mc.listConnections(attr))
        conControlAttr = common.getFirstIndex(mc.listConnections(attr, p=1))
        if control == conControl:
            print('disconnecting', controlAttr, attr)
            mc.disconnectAttr(controlAttr, attr)

def getPoses(poseInterp):
    poses = mc.poseInterpolator(poseInterp, q=1, poseNames=1)
    return(poses)

def getPoseIndexes(poseInterp):
    poseIndexes = mc.poseInterpolator(poseInterp, q=1, index=1)
    return(poseIndexes)

def getPoseIndex(poseInterp, pose):
    index = mm.eval('poseInterpolatorPoseIndex("{}", "{}")'.format(poseInterp, pose))
    if index != -1:
        return(int(index))

def getPoseShapeIndex(poseInterp, pose):
    bs = getDeformer(poseInterp)
    if not bs:
        return
    poseIndex = getPoseIndex(poseInterp, pose)
    connectedTarget = mc.listConnections(poseInterp+'.output[{}]'.format(poseIndex), p=1)
    if connectedTarget:
        targetName = connectedTarget[0].split('.')[1]
        index = getBlendshapeTargetIndex(targetName, bs)
        return(index)

def getBlendshapeTargetIndex(target, bs):
    targetCount = mc.blendShape(bs, q=1, target=1, wc=1)

    i = 0
    n = 0
    while n < targetCount:
        alias = mc.aliasAttr(bs + '.w[{}]'.format(i), q=1)
        if alias == target:
            return i
        if alias:
            n += 1
        i += 1

def updatePose(poseInterp, poseName):
    '''

    :param poseInterp: Pose interpolator transform
    :param poseName: Name of pose
    :return: None
    '''
    mm.eval('poseInterpolator -edit -updatePose {poseName} {poseInterp}'.format(poseInterp=poseInterp,
                                                                                poseName=poseName))
def getPoseName(poseInterp, poseIndex):
    '''

    :param poseInterp:
    :param poseIndex:
    :return:
    '''
    pass

def getDrivers(poseInterp):
    drivers = mc.poseInterpolator(poseInterp, q=1, drivers=1)
    return(drivers)

def getPoseControls(poseInterp):
    driversData = mc.ls(poseInterp + '.driver[*]')
    driverData = driversData[0]
    poseControlData = mc.listAttr(driverData + '.driverController', m=1)
    if not poseControlData:
        return(list())
    poseControls = list()
    for control in poseControlData:
        connectedControls = mc.listConnections(poseInterp + '.%s' % control, p=1)
        if connectedControls:
            poseControls += connectedControls
    return(poseControls)

def getPoseControlData(poseInterp, pose):
    index = getPoseIndex(poseInterp, pose)
    if not index:
        return
    poseControlData = mc.ls('{}.pose[{}].poseControllerData[*]'.format(poseInterp, index))
    poseControlValues = list()
    for data in poseControlData:
        name = mc.getAttr(data + '.poseControllerDataItemName')
        type = mc.getAttr(data + '.poseControllerDataItemType')
        value = mc.getAttr(data + '.poseControllerDataItemValue')
        poseControlValues.append([name, type, value])
    return(poseControlValues)

def getDeformer(poseInterp):
    # Mel call
    # poseInterpolatorConnectedShapeDeformers

    poseInterp = getPoseInterp(poseInterp)
    poses = getPoses(poseInterp)
    indexes = getPoseIndexes(poseInterp)
    for pose, index in zip(poses, indexes):
        con = mc.listConnections(poseInterp+'.output[{index}]'.format(index=index))
        if con:
            if mc.nodeType(con[0]) == 'blendShape':
                return(con[0])

def addPose(poseInterp, pose, type='swing'):
    '''

    :param poseInterp: Pose interpolator
    :param pose: Pose name
    :param type: options are: swing, twist, and swingandtwist
    :return: Index of added pose
    '''
    index = mm.eval('poseInterpolatorAddPose("{poseInterp}", "{pose}")'.format(poseInterp=poseInterp,
                                                                               pose=pose))
    mm.eval('poseInterpolatorSetPoseType("{poseInterp}", "{pose}", "{type}")'.format(poseInterp=poseInterp,
                                                                                     pose=pose,
                                                                                     type=type))
    return index

def goToPose(poseInterp, pose):
    mm.eval('poseInterpolatorGoToPose "{}" "{}"'.format(poseInterp, pose))

def goToNeutralPose(poseInterp):
    poses = getPoses(poseInterp)
    for pose in poses:
        if pose == 'neutral':
            goToPose(poseInterp, pose)

def updatePose(poseInterp, pose):
    mm.eval('poseInterpolatorUpdatePose "{}" "{}"'.format(poseInterp, pose))

def syncPose(poseInterp, pose):
    goToPose(poseInterp, pose)
    updatePose(poseInterp, pose)

def setPoseKernalFalloff(poseInterp, pose):
    '''
    Auto adjusts the gaussian falloff for a more normalized overlap between poses
    :param poseInterp: Pose interpolator
    :param pose: Pose name
    :return: None
    '''
    mm.eval('poseInterpolatorCalcKernelFalloff"{}" "{}"'.format(poseInterp, pose))

def addShape(poseInterp, pose, bs=None):
    poseInterp = getPoseInterp(poseInterp)

    if not bs:
        bs = getDeformer(poseInterp)
    if not bs:
        return

    shapeIndex = mm.eval('doBlendShapeAddTarget("{bs}", 1, 1, "", 0, 0, {{}})'.format(bs=bs))[0]
    mc.aliasAttr(pose, bs+'.w[{index}]'.format(index=shapeIndex))

    poseIndex = getPoseIndex(poseInterp, pose)
    mc.connectAttr(poseInterp+'.output[{}]'.format(poseIndex), bs+'.w[{}]'.format(shapeIndex))
