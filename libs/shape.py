'''
This module is for dealing with shape nodes in Maya
'''
import maya.cmds as mc 

def getDeltas(base, target): 
    '''
    Get deltas between two shapes. 
    Currently it only returns the deltas on the x axis, so when tugging
    the target move it in the positive x axis for yanking.

    :param base: Base object
    :type base: str
    
    :param target: Target object
    :type target: str

    :returns: List of tuples [(pntIndex, value),...]
    :rtype: List
    '''
     
    bs = mc.blendShape(target, base, w=[0, 1])[0] 
    #mc.pointPosition(base+'.vtx[0]') # Enforce refresh
    mc.pointPosition(target+'.vtx[0]') # Enforce refresh 
    delta_list = mc.getAttr(bs+'.it[0].itg[0].iti[6000].ipt')
    index_list = mc.getAttr(bs+'.it[0].itg[0].iti[6000].ict')                                
    mc.delete(bs)
    if not index_list:
        return([])
 
    # =============================================== 
    # Point array 
    # =============================================== 

    count = len(index_list) 
    index_flat_list = list() 
    for n in index_list: 
        index_flat_list.append(target+'.'+n) 
     
    index_flat_list = mc.ls(index_flat_list, fl=1) 
    index_only_list = list() 
     
    for n in index_flat_list: 
        index_only_list.append(n.split('[')[1][:-1]) 
     
    # =============================================== 
    # Weight array 
    # ===============================================     
    weight_list = list()                       
    for n in range(len(index_flat_list)): 
        weight_list.append([ index_flat_list[n].split('[')[1][:-1], delta_list[n][0] ]) 
     
    return(weight_list) 
