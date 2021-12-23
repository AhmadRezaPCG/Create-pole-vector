###############################################################################
# Name: 
#   PoleVector
#
# Description: 
#    this code find pole vector place and create a locator . later you can polevectorconstraint thist locator with ikhandle .
#    
#
# Author: 
#   Ahmadreza Rezaei
#
# Copyright (C) 2022 Ahmadreza Rezaei. All rights reserved.
###############################################################################

import maya.cmds as cmds
import maya.OpenMayaUI as omui
import maya.OpenMaya as om

from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

def maya_main_window():
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window),QtWidgets.QWidget)
    
class polevectorclass(QtWidgets.QDialog):
    
    dialog_open=None
    
    @classmethod
    def show_dialog(cls):
        
        if cls.dialog_open:
            if cls.dialog_open.isHidden():
                cls.dialog_open.show()
            else:
                cls.dialog_open.raise_()
                cls.dialog_open.activateWindow()
        else:
            cls.dialog_open = polevectorclass()
            cls.dialog_open.show()
    
    
    def __init__(self,parent=maya_main_window()):
        super(polevectorclass,self).__init__(parent)
        
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        
        self.setWindowTitle("Create Pole Vector")
        self.setMinimumSize(600,100)
        self.creaLEwidget()
        self.creaLElayout()
        self.connectsignalslot()
    
    def creaLEwidget(self):
        
        self.LE_startjnt = QtWidgets.QLineEdit()
        self.LE_startjnt.setEnabled(False)
        self.LE_startjnt.setPlaceholderText("Start_JNT")
        self.LE_midjnt = QtWidgets.QLineEdit()
        self.LE_midjnt.setPlaceholderText("Mid_JNT")
        self.LE_midjnt.setEnabled(False)
        self.LE_endjnt = QtWidgets.QLineEdit()
        self.LE_endjnt.setEnabled(False)
        self.LE_endjnt.setPlaceholderText("End_JNT")
        self.DS_distance = QtWidgets.QDoubleSpinBox()
        self.DS_distance.setValue(1.00)
        
        self.PB_clear = QtWidgets.QPushButton("Clear Lineedits")
        self.PB_set = QtWidgets.QPushButton("set selection")
        self.PB_create = QtWidgets.QPushButton("create")
    
    def creaLElayout(self):
        
        HL_text = QtWidgets.QHBoxLayout()
        HL_text.addWidget(self.LE_startjnt)
        HL_text.addWidget(self.LE_midjnt)
        HL_text.addWidget(self.LE_endjnt)
        HL_text.addWidget(self.DS_distance)

        HL_button = QtWidgets.QHBoxLayout()
        HL_button.addWidget(self.PB_clear)
        HL_button.addWidget(self.PB_set)
        HL_button.addWidget(self.PB_create)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(HL_text)
        main_layout.addLayout(HL_button)
        
    def connectsignalslot(self):
        
        self.PB_clear.clicked.connect(self.clear_line_edit)
        self.PB_set.clicked.connect(self.set_selection)
        self.PB_create.clicked.connect(self.create_polevector)
        
    def clear_line_edit(self):
        
        self.LE_endjnt.clear()
        self.LE_midjnt.clear()
        self.LE_startjnt.clear()
        
    def set_selection(self):
        
        list_selection = cmds.ls(selection=True)
        bool_check_selection = self.check_selction(list_selection)
        if bool_check_selection : self.setselected_to_lineedit(list_selection)
            
        
    def check_selction(self,ls):
        
        if len(ls) == 3:
            for selected in ls:
                if cmds.objectType(selected) == "joint":
                    continue
                else:
                    om.MGlobal.displayError("Select Joints")
                    return False
        else:
            om.MGlobal.displayError("Just select three Joint")
            return False
        
        return True
                
    def setselected_to_lineedit(self,list_selection):
        
        self.LE_startjnt.setText(list_selection[0])
        self.LE_midjnt.setText(list_selection[1])
        self.LE_endjnt.setText(list_selection[2])
                
    def create_polevector(self):
        
        if self.check_lineeditexist() : 
            list_joint = self.pickup_joint()
        else:
            return
        self.create_pole(list_joint)
        
    def check_lineeditexist(self):
        
        text_end_jnt = self.LE_endjnt.text()
        print text_end_jnt
        if text_end_jnt == "":
            om.MGlobal.displayError("Select joints and click set selection to entire joint")
            return False
        else:
            return True
            
    def pickup_joint(self):
        
        list_joints = [self.LE_startjnt.text(),self.LE_midjnt.text(),self.LE_endjnt.text()]
        return list_joints
        
    def create_pole(self,list_joints):
        
        A = cmds.xform(list_joints[0],q=True,translation=True,ws=True)
        B = cmds.xform(list_joints[1],q=True,translation=True,ws=True)
        C = cmds.xform(list_joints[2],q=True,translation=True,ws=True)
        
        A_point = om.MPoint(A[0],A[1],A[2])
        B_point = om.MPoint(B[0],B[1],B[2])
        C_point = om.MPoint(C[0],C[1],C[2])
        
        AB_point = B_point - A_point
        AC_point = C_point - A_point
        
        length_AD = (AB_point*AC_point)/AC_point.length()
        AD_point = AC_point.normal()*length_AD
        
        D_point = A_point + AD_point
        DB_point = B_point - D_point
        normal_DB = DB_point.normal()
        distance = self.DS_distance.value()
        target_point = D_point+(normal_DB * distance)
        
        name_loc = list_joints[1]+"_polevector"
        numb = 0
        while cmds.objExists(name_loc):
            name_loc = list_joints[1]+"_polevector_"+str(numb)
            numb+=1
            
        cmds.spaceLocator(name = name_loc)
        cmds.setAttr(name_loc+".tx",target_point.x)
        cmds.setAttr(name_loc+".ty",target_point.y)
        cmds.setAttr(name_loc+".tz",target_point.z)
        
if __name__ == "__main__":
    
    try:
        #this line when it wants to close , display error .for disable error we use this method
        dialog.close()  #pylint:disable=E0601
        
        dialog.deleLELaLEr()
    except:
        pass
    
    dialog = creaLEdialog()
    dialog.show()
    

