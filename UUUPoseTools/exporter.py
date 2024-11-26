import bpy

from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from bpy.types import Operator
from mathutils import Quaternion, Vector

from .helpers import bone_tree, get_bone_matrix, get_bone_remap_dict, pretty_print_float

def make_unreal_loc(bone):
    pose_bone_matrix = get_bone_matrix(bone)
    
    return pose_bone_matrix.to_translation() * Vector((1, -1, 1))

def make_unreal_quat(bone):
    pose_bone_matrix = get_bone_matrix(bone)
    
    rotation = pose_bone_matrix.to_quaternion().normalized()
        
    if bone.parent is not None:
        rotation.conjugate()

    return rotation * Quaternion((1, 1, -1, 1))

def write_bonetree(context, uuu_pose, idx):
    for bone in context.active_object.pose.bones:
        parents = "\t" * len(bone.parent_recursive)
        name = bone.name
        
        remap = get_bone_remap_dict("Export").get(name)
        if remap is not None:
            name = remap
        
        combined_name = f"{parents}{idx}:{name}"
        
        line = [combined_name]
        for float in make_unreal_loc(bone):
            line.append(pretty_print_float(float))
        for float in make_unreal_quat(bone):
            line.append(pretty_print_float(float))
        for float in bone.scale:
            line.append(pretty_print_float(float))
        
        uuu_pose.writelines(",".join(line)+"\n")

def export_pose(context, filepath):
    with open(filepath, "w") as posefile:
        posefile.writelines("Bone name,x,y,z,qW,qX,qY,qZ,scaleX,scaleY,scaleZ\n")
        
        # TODO: Improve the manner in which propogation is handled
        propogateToTrees = True
        numTrees = 3
        if propogateToTrees:
            for idx in range(numTrees):
                write_bonetree(context, posefile, idx)
        else:
            write_bonetree(context, posefile, bone_tree)
    
    return {'FINISHED'}

class UUU_OP_ExportPose(Operator, ExportHelper):
    """Exports a pose from the active armature to a .uuupose file."""
    bl_idname = "uuupose.export"
    bl_label = "Export UUU Pose"
    
    filename_ext = ".uuupose"
    
    filter_glob: StringProperty(
        default="*.uuupose",
        options={"HIDDEN"}
    )
    
    @classmethod
    def poll(cls, context):
        return context.active_object.type == "ARMATURE"
    
    def execute(self, context):
        return export_pose(context, self.filepath)