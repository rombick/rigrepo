'''
'''
import maya.cmds as mc
import rigrepo.templates.archetype.rig.build.archetype_base_rig as archetype_base_rig
import pubs.pNode
from rigrepo.libs.fileIO import joinPath 
import rigrepo.nodes.loadFileNode
import rigrepo.nodes.newSceneNode
import rigrepo.nodes.importDataNode
import rigrepo.nodes.exportDataNode
import rigrepo.nodes.yankClusterNode
import rigrepo.nodes.utilNodes 
# body parts import
import rigrepo.parts.arm
import rigrepo.parts.leg
import rigrepo.parts.spine 
import rigrepo.parts.neck
import rigrepo.parts.hand
import rigrepo.parts.foot

# face parts import
import rigrepo.parts.mouth
import rigrepo.parts.blink
import rigrepo.parts.face
import rigrepo.parts.brow
import rigrepo.parts.tongue

import rigrepo.nodes.controlDefaultsNode as controlDefaultsNode
import os

class BipedBaseRig(archetype_base_rig.ArchetypeBaseRig):
    def __init__(self,name, variant='base'):
        '''
        This is the constructor for the biped template. Here is where you will put nodes onto 
        the graph. 

        :param name: Name of the element you're using this for
        :type name: str

        :param variant: Name of the variant this template is being used for.
        :type variant: str
        '''
        
        super(BipedBaseRig, self).__init__(name, variant)

        animRigNode = self.getNodeByName("animRig")

        buildPath = joinPath(os.path.dirname(__file__), self.variant)


        # Parts
        #-------------------------------------------------------------------------------------------
        # BODY
        #-------------------------------------------------------------------------------------------
        # center
        pSpine = rigrepo.parts.spine.Spine(name='pSpine', jointList="mc.ls('spine_*_bind')")
        pSpine.setNiceName("spine")

        pNeck = rigrepo.parts.neck.Neck(name='pNeck', 
                                        jointList="mc.ls('neck_?_bind')", 
                                        anchor="chest_top")
        pNeck.setNiceName("neck")
        
        # Arm
        l_arm = rigrepo.parts.arm.Arm("l_arm", 
                                    ['clavicle_l_bind', 
                                        'shoulder_l_bind', 
                                        'elbow_l_bind', 
                                        'wrist_l_bind'], 
                                    anchor='chest_top')
        l_arm.getAttributeByName("fkControls").setValue(["shoulder_fk_l","elbow_fk_l", "wrist_fk_l"]) 
        l_arm.getAttributeByName("ikControls").setValue(["arm_pv_l","arm_ik_l"])
        l_arm.getAttributeByName("paramNode").setValue("arm_L")
        l_arm.getAttributeByName("clavicleCtrl").setValue("clavicle_l")

        l_hand = rigrepo.parts.hand.Hand("l_hand",
                                        ['ring_001_l_bind', 
                                        'middle_001_l_bind', 
                                        'index_001_l_bind', 
                                        'pinkyCup_l_bind', 
                                        'thumbCup_l_bind'])
        # Auto clavicle
        side = 'l'
        l_autoClav = rigrepo.parts.autoParent.AutoParent(side+'_autoClav',
                                                         parentControl='clavicle_'+side,
                                                         inputControls=['shoulderSwing_'+side,
                                                                        'shoulder_fk_'+side],
                                                         ikJointList=['shoulder_'+side+'_bind_ik',
                                                                      'elbow_'+side+'_bind_ik',
                                                                      'wrist_'+side+'_bind_ik'],
                                                         autoBlendAttr='autoClav',
                                                         side=side,
                                                         ikBlendAttr=side+'_arm_rvr.output.outputX',
                                                         anchor=side+'_arm_anchor_grp')
        # add hand to arm node.
        l_arm.addChildren([l_hand, l_autoClav])

        r_arm = rigrepo.parts.arm.Arm("r_arm",
                                    ['clavicle_r_bind', 
                                     'shoulder_r_bind',
                                     'elbow_r_bind',
                                     'wrist_r_bind'],
                                    anchor='chest_top', 
                                    side='r')

        r_arm.getAttributeByName("fkControls").setValue(["shoulder_fk_r","elbow_fk_r", "wrist_fk_r"]) 
        r_arm.getAttributeByName("ikControls").setValue(["arm_pv_r","arm_ik_r"])
        r_arm.getAttributeByName("paramNode").setValue("arm_R")
        r_arm.getAttributeByName("clavicleCtrl").setValue("clavicle_r")
        
        

        r_hand = rigrepo.parts.hand.Hand("r_hand",
                                        ['ring_001_r_bind', 
                                            'middle_001_r_bind', 
                                            'index_001_r_bind', 
                                            'pinkyCup_r_bind', 
                                            'thumbCup_r_bind'], 
                                        'wrist_r_bind_blend')

        # Auto clavicle
        side = 'r'
        r_autoClav = rigrepo.parts.autoParent.AutoParent(side+'_autoClav',
                                                         parentControl='clavicle_'+side,
                                                         inputControls=['shoulderSwing_'+side,
                                                                        'shoulder_fk_'+side],
                                                         ikJointList=['shoulder_'+side+'_bind_ik',
                                                                      'elbow_'+side+'_bind_ik',
                                                                      'wrist_'+side+'_bind_ik'],
                                                         autoBlendAttr='autoClav',
                                                         side=side,
                                                         ikBlendAttr=side+'_arm_rvr.output.outputX',
                                                         anchor=side+'_arm_anchor_grp')
        # add hand to arm node.
        r_arm.addChildren([r_hand, r_autoClav])

        # Leg
        l_leg = rigrepo.parts.leg.Leg("l_leg",
                                ['pelvis_l_bind', 'thigh_l_bind', 'knee_l_bind', 'ankle_l_bind'], 
                                pSpine.getHipSwivelCtrl)

        l_leg.getAttributeByName("side").setValue("l")
        l_leg.getAttributeByName("fkControls").setValue(["thigh_fk_l","knee_fk_l", "ankle_fk_l"]) 
        l_leg.getAttributeByName("ikControls").setValue(["leg_pv_l","leg_ik_l"])
        l_leg.getAttributeByName("paramNode").setValue("leg_L")
        l_leg.getAttributeByName("clavicleCtrl").setValue("pelvis_l")

        l_foot = rigrepo.parts.foot.Foot("l_foot", ['ankle_l_bind', 'ball_l_bind', 'toe_l_bind'], 
                                        'ankle_l_bind_ik_hdl', 
                                        fkAnchor='ankle_fk_l', 
                                        ikAnchor='ankle_l_bind_ik_offset', 
                                        anklePivot='ankle_l_pivot', 
                                        ankleStretchTarget="ankle_l_bind_ik_tgt",
                                        ikfkGroup='l_leg_ikfk_grp')
        # add foot to the leg node
        l_leg.addChild(l_foot)

        r_leg = rigrepo.parts.leg.Leg("r_leg",
                                ['pelvis_r_bind', 'thigh_r_bind', 'knee_r_bind', 'ankle_r_bind'], 
                                pSpine.getHipSwivelCtrl,
                                side="r")

        r_leg.getAttributeByName("side").setValue("r")
        r_leg.getAttributeByName("fkControls").setValue(["thigh_fk_r","knee_fk_r", "ankle_fk_r"]) 
        r_leg.getAttributeByName("ikControls").setValue(["leg_pv_r","leg_ik_r"])
        r_leg.getAttributeByName("paramNode").setValue("leg_R")
        r_leg.getAttributeByName("clavicleCtrl").setValue("pelvis_r")

        r_foot = rigrepo.parts.foot.Foot("r_foot", ['ankle_r_bind', 'ball_r_bind', 'toe_r_bind'], 
                                        'ankle_r_bind_ik_hdl', 
                                        fkAnchor='ankle_fk_r', 
                                        ikAnchor='ankle_r_bind_ik_offset', 
                                        anklePivot='ankle_r_pivot',
                                        ankleStretchTarget="ankle_r_bind_ik_tgt",
                                        ikfkGroup='r_leg_ikfk_grp')
        # add foot to the leg node
        r_leg.addChild(r_foot)


        #-------------------------------------------------------------------------------------------
        # FACE
        #-------------------------------------------------------------------------------------------
        faceParts = rigrepo.parts.face.Face("face_parts")
        earClusterNode = rigrepo.nodes.utilNodes.ClusterControlNode("ears")
        earClusterNode.getAttributeByName("nameList").setValue("['ear_l', 'ear_r']")
        earClusterNode.getAttributeByName("geometry").setValue("body_geo")
        earClusterNode.getAttributeByName("parent").setValue("face_upper")
        tongueNode = rigrepo.parts.tongue.Tongue(name='tongue', 
                                        jointList="mc.ls('tongue_?_bind')", 
                                        anchor="jaw")
        faceParts.addChildren([earClusterNode])
        l_blink = rigrepo.parts.blink.BlinkNew("l_blink", anchor="face_upper")
        r_blink = rigrepo.parts.blink.BlinkNew("r_blink",side="r", anchor="face_upper")
        r_blink.getAttributeByName("side").setValue("r")
        mouth = rigrepo.parts.mouth.Mouth("mouth", lipMainCurve='lip_main_curve')
        mouth.getAttributeByName("orientFile").setValue(self.resolveDataFilePath('control_orients.data', self.variant))
        mouthBindGeometry = rigrepo.nodes.commandNode.CommandNode('bindGeometry')
        mouthBindGeometryCmd = '''
import maya.cmds as mc
import rigrepo.libs.cluster
for curve in ["lip_main_curve", "lip_curve"]:
    wireDeformer = "{}_wire".format(curve)
    if mc.objExists(wireDeformer):
        mc.sets(mc.ls("body_geo.vtx[*]")[0], e=True, add="{}Set".format(wireDeformer))
        mc.rename(wireDeformer, curve.replace("_curve", "_wire"))
    else:
        wireDeformer = mc.wire("body_geo", gw=False, en=1.00, ce=0.00, li=0.00, 
                        w=curve, name=curve.replace("_curve", "_wire"))[0]
        # set the default values for the wire deformer
        mc.setAttr("{}.rotation".format(wireDeformer), 0)
        mc.setAttr("{}.dropoffDistance[0]".format(wireDeformer), 100)

bindJointList = list(set(mc.ls("lip_*_baseCurve_jnt")).difference(set(mc.ls("lip_main_*_baseCurve_jnt"))))
skinCluster = mc.skinCluster(*bindJointList + ["lip_curveBaseWire"],
                                rui=False,
                                tsb=True,
                                name="lip_curveBaseWire_skinCluster")[0]

for jnt in bindJointList:
    index = [int(s) for s in jnt.split("_") if s.isdigit()][0]
    mc.skinPercent(skinCluster, "lip_curveBaseWire.cv[{}]".format(index), tv=["lip_{}_baseCurve_jnt".format(index), 1])

for mesh in mc.ls(["lip_main_bindmesh", "lip_bindmesh", "mouth_corner_bindmesh"]):
    if mc.objExists(mesh) and mc.objExists("mouthMain_cls_hdl"):
        mc.select(mesh, r=True)
        cls = mc.cluster(name="{}_mouthMain_cluster".format(mesh), wn=['mouthMain_cls_hdl','mouthMain_cls_hdl'],bs=1)[0]
        rigrepo.libs.cluster.localize(cls, 'mouthMain_auto', 'model')
'''
        mouthBindGeometry.getAttributeByName('command').setValue(mouthBindGeometryCmd)
        mouth.addChildren([mouthBindGeometry])
        controlsDefaults = controlDefaultsNode.ControlDefaultsNode("control_defaults",
                                armControls=["*shoulder","*elbow","*wrist"], 
                                armParams=["arm_?"])
        l_brow = rigrepo.parts.brow.Brow("l_brow", anchor="head_tip")
        r_brow = rigrepo.parts.brow.Brow("r_brow", side="r", anchor="head_tip")
        r_brow_orient = rigrepo.nodes.commandNode.CommandNode('scaleOrients')
        r_brow_orientCmd = '''
import maya.cmds as mc
brow_orients = mc.ls("brow*_r_ort")
brow_nuls = mc.ls("brow*_r_nul")
brow_nul_parents = [mc.listRelatives(nul, p=True)[0] for nul in brow_nuls]
for nul, ort in zip(brow_nuls,brow_orients):
    mc.parent(nul, w=True)
    mc.setAttr("{}.sz".format(ort), -1)
    
for nul,parent in zip(brow_nuls, brow_nul_parents):
    mc.parent(nul, parent)
'''
        r_brow_orient.getAttributeByName('command').setValue(r_brow_orientCmd)
        r_brow.addChild(r_brow_orient)

        cheekClusterNode = rigrepo.nodes.utilNodes.ClusterControlNode("cheeks")
        cheekClusterNode.getAttributeByName("nameList").setValue("['cheekPuff_l', 'cheekPuff_r', 'cheek_l', 'cheek_r']")
        cheekClusterNode.getAttributeByName("geometry").setValue("body_geo")
        cheekClusterNode.getAttributeByName("parent").setValue("face_mid_driver")
        leftCheekLiftClusterNode = rigrepo.nodes.utilNodes.ClusterControlNode("l_cheekLift")
        leftCheekLiftClusterNode.getAttributeByName("nameList").setValue("['cheekLift_l']")
        leftCheekLiftClusterNode.getAttributeByName("geometry").setValue("body_geo")
        leftCheekLiftClusterNode.getAttributeByName("parent").setValue("lidLower_l")
        rightCheekLiftClusterNode = rigrepo.nodes.utilNodes.ClusterControlNode("r_cheekLift")
        rightCheekLiftClusterNode.getAttributeByName("nameList").setValue("['cheekLift_r']")
        rightCheekLiftClusterNode.getAttributeByName("geometry").setValue("body_geo")
        rightCheekLiftClusterNode.getAttributeByName("parent").setValue("lidLower_r")
        mouthCornerDistanceNode = rigrepo.nodes.commandNode.CommandNode('mouthCornerDistance')
        mouthCornerDistanceNodeCmd = '''
import maya.cmds as mc
for side in ["l","r"]:
    distanceLoc = mc.createNode("transform", n="distance_loc_{}".format(side))
    mc.xform(distanceLoc, ws=True, matrix=mc.xform("eye_{}_bind".format(side), q=True, ws=True, matrix=True))
    mc.parent(distanceLoc, "face_upper")
    mouthCornerDCM = mc.createNode("decomposeMatrix", name="mouth_corner_{}_decomposeMatrix".format(side))
    distanceLocDCM = mc.createNode("decomposeMatrix", name="distance_loc_{}_decomposeMatrix".format(side))
    
    mc.connectAttr("mouth_corner_{}.worldMatrix[0]".format(side), "{}.inputMatrix".format(mouthCornerDCM))
    mc.connectAttr("distance_loc_{}.worldMatrix[0]".format(side), "{}.inputMatrix".format(distanceLocDCM))
    
    distanceNode = mc.createNode("distanceBetween", n="mouth_corner_{}_distance".format(side))
    mc.connectAttr("{}.outputTranslate".format(mouthCornerDCM), "{}.point1".format(distanceNode), f=True)
    mc.connectAttr("{}.outputTranslate".format(distanceLocDCM), "{}.point2".format(distanceNode), f=True)
        

    currentDistance = mc.getAttr("{}.distance".format(distanceNode))        
    for axis in ['x', 'y', 'z']:
        mc.setDrivenKeyframe("cheekPuff_{}_def_auto.s{}".format(side, axis), 
                                    cd="{}.distance".format(distanceNode), v=1, dv=currentDistance)
        mc.setDrivenKeyframe("cheekPuff_{}_def_auto.s{}".format(side, axis), 
                                    cd="{}.distance".format(distanceNode), v=2, dv=currentDistance-2)
                                    
                                    
        if axis == "y":
            mc.setDrivenKeyframe("cheek_{}_def_auto.t{}".format(side, axis), 
                                        cd="{}.distance".format(distanceNode), v=0, dv=currentDistance)
            mc.setDrivenKeyframe("cheek_{}_def_auto.t{}".format(side, axis), 
                                        cd="{}.distance".format(distanceNode), v=2, dv=currentDistance-2)

    # lid lower rotation
    mc.setDrivenKeyframe("lidLower_{}_def_auto.rx".format(side), 
                                    cd="{}.distance".format(distanceNode), v=0, dv=currentDistance)
    mc.setDrivenKeyframe("lidLower_{}_def_auto.rx".format(side), 
                                    cd="{}.distance".format(distanceNode), v=6, dv=currentDistance-2)

    if mc.objExists("cheekLift_{}_def_auto".format(side)):
        mc.setDrivenKeyframe("cheekLift_{}_def_auto.rx".format(side), 
                                        cd="{}.distance".format(distanceNode), v=0, dv=currentDistance)
        mc.setDrivenKeyframe("cheekLift_{}_def_auto.rx".format(side), 
                                        cd="{}.distance".format(distanceNode), v=6, dv=currentDistance-2)

        mc.addAttr("lidLower_{}".format(side), ln="cheekLift", at="double", keyable=True)
        mc.setDrivenKeyframe("cheekLift_{}.rx".format(side), 
                                        cd="lidLower_{}.cheekLift".format(side), v=0, dv=0)
        mc.setDrivenKeyframe("cheekLift_{}.rx".format(side), 
                                        cd="lidLower_{}.cheekLift".format(side), v=50, dv=10)
        mc.setDrivenKeyframe("cheekLift_{}.rx".format(side), 
                                        cd="lidLower_{}.cheekLift".format(side), v=-50, dv=-10)

        # turn off display handles for cheek lift
        mc.setAttr("cheekLift_{}_def_auto.displayHandle".format(side), 0)
                
'''
        mouthCornerDistanceNode.getAttributeByName('command').setValue(mouthCornerDistanceNodeCmd)
        cheekClusterNode.addChildren([leftCheekLiftClusterNode, rightCheekLiftClusterNode, mouthCornerDistanceNode])

        # create both face and body builds
        bodyBuildNode = pubs.pNode.PNode("body")
        faceBuildNode = pubs.pNode.PNode("face")

        browsNode = pubs.pNode.PNode("brows")
        browsNode.addChildren([l_brow, r_brow])

        eyesNode = pubs.pNode.PNode("eyes")
        eyesNode.addChildren([l_blink, r_blink])

        
        # add nodes ass children of body
        bodyBuildNode.addChildren([pSpine, pNeck, l_arm, r_arm, l_leg, r_leg])
        faceBuildNode.addChildren([faceParts, tongueNode, browsNode, eyesNode, mouth, cheekClusterNode])

        # get the load node which is derived from archetype.
        loadNode = self.getNodeByName('load')
        #loadNode.addChildren([curveFileNode, curveDataNode])

        # get the postBuild node
        postBuild = animRigNode.getChild('postBuild')
        postBuild.addChild(controlsDefaults)

        applyDeformerNode = animRigNode.getChild('apply').getChild('deformers')
        bindmeshTransferSkinWtsNode = rigrepo.nodes.transferDeformer.TransferDeformerBindmesh('bindmesh', 
                                                            source="body_geo",
                                                            target=["lid*_bindmesh", "lip*_bindmesh", "mouth*_bindmesh"],
                                                            deformerTypes = ["skinCluster"],
                                                            surfaceAssociation="closestPoint")
        bindmeshTransferClusterBlinksNode = rigrepo.nodes.transferDeformer.TransferClusterBlinks('transferBlinkClusters', 
                                                            source="body_geo")
        bindmeshTransferClusterLidsNode = rigrepo.nodes.transferDeformer.TransferClusterLids('transferLidsClusters', 
                                                            source="body_geo")
        freezeWireNode = rigrepo.nodes.goToRigPoseNode.GoToFreezePoseNode('freezeWire')

        lipYankNode = rigrepo.nodes.yankClusterNode.YankClusterNode('WireToClusters',
                                                    clusters='[trs+"_cluster" for trs in mc.ls("lip_*.__control__", o=True)]',
                                                    transforms='mc.ls("lip_*.__control__", o=True)',
                                                    selected=False,
                                                    geometry="body_geo")
        applyWireNode = applyDeformerNode.getChild("wire")
        applyWireNode.addChildren([freezeWireNode, lipYankNode])


        applyDeformerNode.addChildren([bindmeshTransferSkinWtsNode], 1)
        applyDeformerNode.addChildren([bindmeshTransferClusterBlinksNode, bindmeshTransferClusterLidsNode], 4)
        
    
        # create a build node to put builds under.
        buildNode = pubs.pNode.PNode("build")
        # add nodes to the build
        buildNode.addChildren([bodyBuildNode, faceBuildNode])

        # add children to the animRigNode
        animRigNode.addChildren([buildNode], 
                                index=postBuild.index())

        l_leg.getAttributeByName('anchor').setValue('hip_swivel')
        r_leg.getAttributeByName('anchor').setValue('hip_swivel')
