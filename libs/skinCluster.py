'''
This module is for dealing with skinClusters inside Maya
'''
import maya.cmds as mc

import rigrepo.libs.common

def localize(skinClusters, transform):
    '''
    Localize skinCluster to the given transform

    :param skinCluster: skinCluster to localize
    :type skinCluster: str or list

    :param transform: Transform to localize against
    :type transform: str
    '''
    if not mc.objExists(transform):
        raise RuntimeError("{} doesn't exist in the current Maya session.".format(transform))

    transformDescedants = mc.listRelatives(transform, ad=True, type="transform")
    if isinstance(skinClusters, basestring):
        skinClusters = rigrepo.libs.common.toList(skinClusters)
    for skinCluster in skinClusters:
        infs = mc.skinCluster(skinCluster, q=True, inf=True)
        geoTransform = mc.listRelatives(mc.skinCluster(skinCluster, q=True, geometry=True)[0], p=True)[0]
        if geoTransform not in transformDescedants:
            transform = geoTransform
        if not infs:
            return()
        for inf in infs:
            connection = mc.listConnections(inf+'.worldMatrix[0]', p=1, type='skinCluster')
            for con in connection:
                if skinCluster == con.split('.')[0]:
                    index = con.split('[')[1].split(']')[0]
                    # Nothing needs to be done if the bindPreMatrix is hooked up
                    if mc.listConnections('{0}.bindPreMatrix[{1}]'.format(skinCluster, index)):
                        continue
                    multMatrix = '{}__{}_localizeMatrix'.format(inf, skinCluster)
                    if not mc.objExists(multMatrix):
                        multMatrix = mc.createNode('multMatrix', n=multMatrix)
                        mc.setAttr(multMatrix+'.isHistoricallyInteresting', 0)
                    if not mc.isConnected(inf+'.worldMatrix[0]', multMatrix+'.matrixIn[1]'):
                        mc.connectAttr(inf+'.worldMatrix[0]', multMatrix+'.matrixIn[1]', f=1)
                    if not mc.isConnected(transform+'.worldInverseMatrix[0]', multMatrix+'.matrixIn[2]'):
                        mc.connectAttr(transform+'.worldInverseMatrix[0]', multMatrix+'.matrixIn[2]', f=1)
                    if not mc.isConnected(multMatrix+'.matrixSum', con):
                        mc.connectAttr(multMatrix+'.matrixSum', con, f=1)

def getSkinCluster(geometry):
    '''
    This will check the geometry to see if it has a skinCluster in it's histroy stack

    :param geometry: The mesh you want to check for a skinCluster
    :type geometry: str
    '''
    # check the history to see if there is a skinCluster
    hist = [node for node in mc.listHistory(geometry, pdo=True, lv=1) if mc.nodeType(node) == "skinCluster"]
    # make an emptry str so we return a str no matter what.
    skinCluster = str()

    # if there is a skinCluster in the hist. we will set it skinCluster to it.
    if hist:
      skinCluster = hist[0]

    return skinCluster

def transferSkinCluster(source, target, surfaceAssociation="closestPoint"):
    '''
    This will transfer skinCluster from one mesh to another. If the target doesn't have a 
    skinCluster on it, it will create a new skinCluster. Then once there is a skinCluster
    We will copy weights over.

    :param source: The geomertry you are transfer from
    :type source:  str

    :param target: The geometry you want to transfer to
    :type target: str | list

    :param surfaceAssociation: How to copy the weights from source to target available values 
                                are "closestPoint", "rayCast", or "closestComponent"
    :type surfaceAssociation: str
    '''
    # do some error checking
    if not mc.objExists(source):
        raise RuntimeError('The source mesh "{}" does not exist in the current Maya session.'.format(source))
    if not isinstance(surfaceAssociation, basestring):
        raise TypeError('The surfaceAssociation argument must be a string.')

    # first we will turn the target into a list if it's not already a list
    meshList = rigrepo.libs.common.toList(target)
    
    # make sure we have a skinCluster on the source mesh 
    sourceSkinCluster = getSkinCluster(source)
    skinClusterList = list()
    for mesh in meshList:
        if not mc.objExists(mesh):
            mc.warning('The target mesh "{}" does not exist in the current Maya session.'.format(target))
            continue

        # check to see if there is a skinCluster already  on the target mesh
        hist = [node for node in mc.listHistory(mesh, pdo=True, lv=1) if mc.nodeType(node) == "skinCluster"]

        # if there is no skinCluster, we will create one.
        if not hist:
            skinClusterList.append(mc.skinCluster(*mc.skinCluster(sourceSkinCluster, 
                                                q=True, 
                                                inf=True) + [mesh], 
                                            rui=False,
                                            tsb=True,
                                            name="{}_skinCluster".format(mesh))[0])
        else:
            skinClusterList.append(hist[0])


        # now we will transfer the wts
        mc.copySkinWeights(ss=sourceSkinCluster, ds=skinClusterList[-1], 
                                sa=surfaceAssociation, noMirror=True,
                                influenceAssociation=["oneToOne", "name", "closestJoint"], 
                                normalize=True)
      

    return skinClusterList
