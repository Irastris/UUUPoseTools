bone_remap_dict = {
    "Root": "root",
    "Pelvis": "pelvis",
    "Hand_L": "hand_l",
    "Hand_R": "hand_r",
}

bone_tree = 0

def get_bone_matrix(bone):
    matrix = bone.matrix
    
    if bone.parent:
        matrix = bone.parent.matrix.inverted() @ matrix
    
    return matrix

def get_bone_remap_dict(mode):
    match mode:
        case "Import":
            return bone_remap_dict
        case "Export":
            return dict((v, k) for k, v in bone_remap_dict.items())
        case _:
            return

def pretty_print_float(float):
    str = f"{float:.8f}".rstrip("0")
    if str.endswith("."): str += "0"
    return str