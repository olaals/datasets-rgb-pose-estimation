
def pyrender_conf(render_normal=False, render_depth=False):
    return {
        "name":"pyrender",
        "render_normal":render_normal,
        "render_depth":render_depth,
    }


def metal_sampler(chemical_symbol, log_roughness_min, log_roughness_max, probability_weight=1.0):
    return {
        "type": "metal_sampler",
        "chemical_symbol": chemical_symbol,
        "log_roughness_min": log_roughness_min,
        "log_roughness_max": log_roughness_max,
        "probability_weight": probability_weight,
    }

def texture_sampler(texture_type, probability_weight=1.0):
    return {
        "type": "texture_sampler",
        "texture_type": texture_type,
        "probability_weight": probability_weight,
    }

def blender_pbr_sampler(pbr_type, probability_weight, roughness_range=(0.3,1.0)):
    return {
        "type": "pbr",
        "pbr_type": pbr_type,
        "probability_weight": probability_weight,
        "roughness_range": roughness_range
    }

def blender_metal_sampler(probability_range, roughness_range=(0.3,1.0), base_color_range=(0.2,0.4)):
    return {
        "type": "bsdf-metal",
        "probability_weight": probability_range,
        "roughness_range": roughness_range,
        "base_color_range": base_color_range,
    }

