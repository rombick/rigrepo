
import maya.cmds as mc
import maya.api.OpenMaya as om
import rigrepo.libs.transform

def createCurveFromPoints(points, degree=3, name='curve'):
        '''
        :param points: Points you wish to use to create a curve
        :type points: list

        :param degree: The degree of the curve you want to create
        :type degree: int

        :param name: the name of the curve.
        :type name: str

        :return: The name of the curve that was created.
        :rtype: str
        '''
        knotList = [0]
        if degree == 1:
            knotList.extend(range(len(points))[1:])
        elif degree == 2:
            knotList.extend(range(len(points) - 1))
            knotList.append(knotList[-1]) 
        elif degree == 3:
            knotList.append(0) 
            knotList.extend(range(len(points) - 2))
            knotList.extend([knotList[-1],knotList[-1]]) 
        
        curve = mc.curve(name=name, p=points,k=knotList,degree=degree)
        
        return curve


#----------------------------------------------------
# get information functions
def getCVs(curve):
    '''
    Returns all of the cv's on a given curve

    :param curve: The name of the curve you wish to get the cv's for.
    :type curve: str

    :return: Returns the list of cv's
    :rtype: list
    '''
    return mc.ls('%s.cv[*]' % curve, flatten = True)
    
    
def getCVpositions(cvList):
    '''
    This funtion will return the positions of the cvs

    :param cvList: The points you wish to get the positions for.
    :type cvList: list

    :return: Positions in world space for the cv's given
    :rtype: list
    '''
    positions = list()
    
    for point in cvList:
        ws = mc.xform(point, q = True, ws = True, t = True)
        positions.append(ws)
    
    return positions

def getParamFromPosition(curve, point):
    '''
    Gets a curves parameter value from a position or object in space
    
    :param curve: Curve you want to get paremter for
    :type curve: *str* or *MObject*
    
    :param point: Point in space or Node to get MPoint from
    :type: list | MPoint
    '''
    #get dag path for curve and assign it a nurbsCurve function object 
    dagPath = rigrepo.libs.transform.getDagPath(curve)
    mFnNurbsCurve = om.MFnNurbsCurve(dagPath)
    
    #Check to see if point is a list or tuple object
    if not isinstance(point, list) and not isinstance(point, tuple):
        if cmds.objExists(point):
            point = cmds.xform(point, q = True, ws = True, t = True)

    
    #Get and MPoint object and a double ptr
    mPoint = om.MPoint(point[0], point[1], point[2])
    
    return mFnNurbsCurve.getParamAtPoint(mPoint)
