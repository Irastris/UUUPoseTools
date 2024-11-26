import bpy
import csv

from bpy_extras.io_utils import ImportHelper
from bpy.props import BoolProperty, StringProperty
from bpy.types import Operator
from mathutils import Quaternion, Vector

from .helpers import bone_tree, get_bone_remap_dict

# TODO: Can this be done without relying on bone properties added by UEFormat?
def make_blender_quat(bone, uuu_quat):
    orig_quat = Quaternion(orig_quat) if (orig_quat := bone.bone.get("orig_quat")) else Quaternion()
    post_quat = Quaternion(post_quat) if (post_quat := bone.bone.get("post_quat")) else Quaternion()
    
    q = post_quat.copy()
    q.rotate(orig_quat)
    
    quat = q
    
    q = post_quat.copy()
    
    if bone.parent is None:
        q.rotate(uuu_quat.conjugated())
    else:
        q.rotate(uuu_quat)
        
    quat.rotate(q.conjugated())
    
    return quat

def import_pose(context, filepath, negate_root):
    with open(filepath) as posefile:
        for i, row in enumerate(csv.reader(posefile, delimiter=",")):
            row[0] = "".join(s for s in row[0] if ord(s)>31 and ord(s)<126) # Strip formatting TABs
            if row[0][0] == str(bone_tree) and row[0][1] == ":": # Only process rows which are for the active bone tree and do not belong to morph targets
                name = row[0][2:]
                
                # NOTE: Bones seem to sometimes change names between their on-disk and runtime counterparts, so I remap them as a workaround.
                remap = get_bone_remap_dict("Import").get(name)
                if remap is not None:
                    name = remap
                
                bone = context.active_object.pose.bones.get(name)
                if bone is None:
                    print(f"Could not find bone for name {name}, skipping.") # NOTE: Log the bone name for easier tracking of bone name that have had their capitalization altered one way or another.
                    continue
                
                # Location
                x = float(row[1])
                y = float(row[2])
                z = float(row[3])
                bone.location = Vector((x, -y, z)) * 0.01 # TODO: Check if scale should be exposed to user for handling non-centimeter scale workflows
                
                # Scale
                x = float(row[8])
                y = float(row[9])
                z = float(row[10])
                bone.scale = Vector((x, y, z))
                
                # Rotation
                w = float(row[7])
                x = float(row[4])
                y = float(row[5])
                z = float(row[6])
                
                if negate_root and name == "root":
                    y = -y
                
                bone.rotation_quaternion = make_blender_quat(bone, Quaternion((w, x, -y, z)))
    
    return {'FINISHED'}

class UUU_OP_ImportPose(Operator, ImportHelper):
    """Imports a pose from a .uuupose file to the active armature."""
    bl_idname = "uuupose.import"
    bl_label = "Import UUU Pose"
    
    filename_ext = ".uuupose"
    
    filter_glob: StringProperty(
        default="*.uuupose",
        options={"HIDDEN"}
    )
    
    negate_root: BoolProperty(
        name="Negate Root",
        description="Negate the rotation of the root bone.",
        default=True
    )
    
    @classmethod
    def poll(cls, context):
        return context.active_object.type == "ARMATURE"
    
    def execute(self, context):
        return import_pose(context, self.filepath, self.negate_root)