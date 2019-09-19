'''
'''
import maya.cmds as mc
import numpy
import rigrepo.libs.weights
import rigrepo.libs.shape

def convertWiresToSkinCluster(newSkinName, targetGeometry, wireDeformerList, keepWires=False, 
    rootParentNode="rig", rootPreMatrixNode="trs_aux", jointDepth=2):
    '''
    This function will take in a wire deformer list and create a new skinCluster

    :param newSkinName: This is the name we will use for the new skinCluster we're creating.
    :type newSkinName: str

    :param targetGeometry: This is the geometry we will be putting the skinCluster onto.
    :type targetGeometry: str
    '''
    target = targetGeometry
    base = mc.duplicate(target)[0]
    convertWireList = mc.ls(wireDeformerList, type="wire")

    # create a target skinCluster that will replace the wire defomer
    targetSkinCluster = mc.deformer(target, type="skinCluster", name=newSkinName)[0]
    # create a base joint that we can put weights on.
    baseJnt = "root_preMatrix_jnt"
    if not mc.objExists(baseJnt):
        mc.createNode("joint",name="root_preMatrix_jnt")
        mc.parent(baseJnt,rootParentNode)

    # get the influences to be used for the target skinCluster
    preMatrixNodeList = list()
    influenceList = list()
    weightList = list()
    curveList = list()

    for wireDeformer in convertWireList:
        # get the curve
        curve = mc.wire(wireDeformer, q=True, wire=True)[0]
        curveList.append(curve)
        # get the skinCluster associated with that curve
        curveSkin = mc.ls(mc.listHistory(curve, il=1, pdo=True), type="skinCluster")[0]
        # get the influences associated with the skinCluster
        curveSkinInfluenceList = mc.skinCluster(curveSkin, q=True, inf=True)
        # get the nuls to use as bindPreMatrix nodes
        curveSkinPreMatrixNodes = list()
        for jnt in curveSkinInfluenceList:
            preMatrixNode = jnt
            for i in xrange(jointDepth):
                parent = mc.listRelatives(preMatrixNode, p=True)[0]
                if i == (jointDepth - 1):
                    curveSkinPreMatrixNodes.append(parent)
                preMatrixNode = parent

        influenceList.extend(curveSkinInfluenceList)
        preMatrixNodeList.extend(curveSkinPreMatrixNodes)

        # connect the influences to the matrices and the nuls as the bind preMatrix
        # YANK IT!!!!!!
        for jnt, preMatrixNode in zip(curveSkinInfluenceList, curveSkinPreMatrixNodes):
            # create a temp influence we will use to connect the curveSkin to
            tempInf = mc.duplicate(jnt, po=1)[0]
            # get the connections through the worldMatrix connection
            matrixCon = mc.listConnections(jnt+'.worldMatrix[0]', p=1, d=1, s=0)
            infIndex = None
            for con in matrixCon:
                node = con.split('.')[0]
                if node == curveSkin:
                    infIndex = con.split('[')[1].split(']')[0]
            if infIndex:
                # connect the temp influence
                mc.connectAttr(tempInf+'.worldMatrix[0]', curveSkin+'.matrix[{}]'.format(infIndex), f=1)
                # move the influence
                mc.move( 1, 0, 0, tempInf, r=1, worldSpaceDistance=1) 
                # get the delta to put into weightList
                weightList.append(rigrepo.libs.shape.getDeltas(base, target))
                # recconect the joint and delete the temp influence.
                mc.connectAttr(jnt+'.worldMatrix[0]', curveSkin+'.matrix[{}]'.format(infIndex), f=1) 
                mc.delete(tempInf)

    # add in
    i=0
    for jnt, preMatrixNode in zip(influenceList,preMatrixNodeList):
        mc.connectAttr("{}.worldMatrix[0]".format(jnt), "{}.matrix[{}]".format(targetSkinCluster, i), f=True)
        mc.connectAttr("{}.worldInverseMatrix[0]".format(preMatrixNode), "{}.bindPreMatrix[{}]".format(targetSkinCluster, i), f=True)
        i += 1
        
    # connect the base joint so we have somewhere to put the weights not being used.
    mc.connectAttr("{}.worldMatrix[0]".format(baseJnt), "{}.matrix[{}]".format(targetSkinCluster, i), f=True)
    mc.connectAttr("{}.worldInverseMatrix[0]".format(rootPreMatrixNode), "{}.bindPreMatrix[{}]".format(targetSkinCluster, i), f=True)
    
    # make sure we have the correct weights for the baseJnt
    baseJntArray = numpy.array([1.0 for id in mc.ls("{}.cp[*]".format(target), fl=True)])
    for weights in weightList:
        baseJntArray = baseJntArray - weights

    # add the baseJnt weights first by itself.
    influenceList.insert(0, baseJnt)
    weightList.insert(0, baseJntArray)
    # then add the rest of the weights
    rigrepo.libs.weights.setWeights(targetSkinCluster, rigrepo.libs.weightObject.WeightObject(maps=influenceList, weights=weightList)) 

    # delete the base that we were using to compare deltas from
    mc.delete(base)

    # delete the wire deformers
    if not keepWires:
        mc.delete(convertWireList+curveList)