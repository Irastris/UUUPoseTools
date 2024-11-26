import bpy
import sys

from .importer import UUU_OP_ImportPose
from .exporter import UUU_OP_ExportPose

bl_info = {
    "name": "UUU pose format",
    "author": "Irastris",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "category": "Import-Export"
}

def draw_import_menu(self, context):
    self.layout.operator(UUU_OP_ImportPose.bl_idname, text="UUU Pose (.uuupose)")

def draw_export_menu(self, context):
    self.layout.operator(UUU_OP_ExportPose.bl_idname, text="UUU Pose (.uuupose)")

operators = (UUU_OP_ImportPose, UUU_OP_ExportPose)

def register():
    for operator in operators:
        bpy.utils.register_class(operator)
    
    bpy.types.TOPBAR_MT_file_import.append(draw_import_menu)
    bpy.types.TOPBAR_MT_file_export.append(draw_export_menu)

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(draw_export_menu)
    bpy.types.TOPBAR_MT_file_import.remove(draw_import_menu)
    
    for operator in reversed(operators):
        bpy.utils.unregister_class(operator)
    
    for k, v in dict(sorted(sys.modules.items(), key=lambda x:x[0])).items():
        if k.startswith(__name__):
            del sys.modules[k]

if __name__ == "__main__":
    register()