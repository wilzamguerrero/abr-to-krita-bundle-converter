#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Freya Lupen <penguinflyer2222@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from enum import IntEnum

import platform
(major, minor, patch) = platform.python_version_tuple()
if int(major) <= 3 and int(minor) < 11:
    from enum import Enum
    class StrEnum(str, Enum):
        def __str__(self):
            return self.value
else:
    # Added in Python 3.11
    from enum import StrEnum

def presetForEngine(paintopId):
        match paintopId:
            case Paintop.Pixel:
                return PixelEnginePreset()
            case Paintop.ColorSmudge:
                return ColorSmudgeEnginePreset()
            case Paintop.QuickBrush:
                return QuickBrushEnginePreset()
            case Paintop.Sketch:
                return SketchEnginePreset()
            case Paintop.Bristle:
                return BristleEnginePreset()
            case Paintop.Shape:
                return ShapeEnginePreset()
            case Paintop.Spray:
                return SprayEnginePreset()
            case Paintop.Hatching:
                return HatchingEnginePreset()
            case Paintop.Grid:
                return GridEnginePreset()
            case Paintop.Curve:
                return CurveEnginePreset()
            case Paintop.Particle:
                return ParticleEnginePreset()
            case Paintop.Clone:
                return CloneEnginePreset()
            case Paintop.Deform:
                return DeformEnginePreset()
            case Paintop.TangentNormal:
                return TangentNormalEnginePreset()
            case Paintop.Filter:
                return FilterEnginePreset()
            case Paintop.MyPaint:
                return MyPaintEnginePreset()
            case None:
                print(f"no paintop, default to Pixel")
                return PixelEnginePreset()
            case _:
                print(f"unknown paintop {paintopId}, default to Pixel")
                return PixelEnginePreset()

class Paintop(StrEnum):
    Pixel         = "paintbrush"
    ColorSmudge   = "colorsmudge"
    QuickBrush    = "roundmarker"
    Sketch        = "sketchbrush"
    Bristle       = "hairybrush"
    Shape         = "experimentbrush"
    Spray         = "spraybrush"
    Hatching      = "hatchingbrush"
    Grid          = "gridbrush"
    Curve         = "curvebrush"
    Particle      = "particlebrush"
    Clone         = "duplicate"
    Deform        = "deformBrush"
    TangentNormal = "tangentnormal"
    Filter        = "filter"
    MyPaint       = "mypaintbrush"

class BrushTipType(StrEnum):
    Auto       = "auto_brush"
    Predefined = "png_brush"
    Text       = "kis_text_brush"
    ABR        = "abr_brush" # imported

class AutoBrushTipShape(IntEnum):
    Circle    = 0
    Rectangle = 1

class AutoBrushTipMaskType(IntEnum):
    Default  = 0
    Soft     = 1
    Gaussian = 2

class AutoBrushGenShape(StrEnum):
    Circle = 'circle',
    Square = 'rct' # rectangle

class AutoBrushGenType(StrEnum):
    Default = 'Default'
    Soft = 'Soft'
    Gaussian = 'Gaussian'

class PredefinedBrushTipMode(IntEnum):
    AlphaMask = 0
    ColorImage = 1
    LightnessMap = 2 
    GradientMap = 3

class BlendingMode(StrEnum):
    # Binary
    XOR                 = "xor"
    OR                  = "or"
    AND                 = "and"
    NAND                = "nand"
    NOR                 = "nor"
    XNOR                = "xnor"
    IMPLICATION         = "implication"
    NOT_IMPLICATION     = "not_implication"
    CONVERSE            = "converse"
    NOT_CONVERSE        = "not_converse"

    # Arithmetic
    Add                 = "add"
    Subtract            = "subtract"
    InverseSubtract     = "inverse_subtract"
    Multiply            = "multiply"
    Divide              = "divide"

    # Negative
    Difference          = "diff"
    Equivalence         = "equivalence"
    AdditiveSubtractive = "additive_subtractive"
    Exclusion           = "exclusion"
    ArcusTangent        = "arc_tangent"
    Negation            = "negation"

    # Modulo
    Modulo                = "modulo"
    ModuleContinuous      = "modulo_continuous"
    DivisiveModulo        = "divisive_modulo"
    DivisiveModuloContinuous = "divisive_modulo_continuous"
    ModuloShift           = "modulo_shift"
    ModuloShiftContinuous = "modulo_shift_continuous"

    # Mix 
    Normal            = "normal"
    Behind            = "behind"
    Greater           = "greater"
    Overlay           = "overlay"
    LambertLighting   = "lambert_lighting"
    LambertLightingGamma2_2 = "lambert_lighting_gamma2.2"
    Erase             = "erase"
    AlphaDarken       = "alphadarken"
    HardMix           = "hard mix"
    HardMixHDR        = "hard_mix_hdr"
    HardMixPhotoshop  = "hard_mix_photoshop"
    HardMixSofterPhotoshop = "hard_mix_softer_photoshop"
    GrainMerge        = "grain_merge"
    GrainExtract      = "grain_extract"
    Parallel          = "parallel"
    Allanon           = "allanon"
    GeometricMean     = "geometric_mean"
    DestinationAtop   = "destination-atop"
    DestinationIn     = "destination-in"
    HardOverlay       = "hard overlay"
    HardOverlayHDR    = "hard_overlay_hdr"
    Interpolation     = "interpolation"
    Interpolation2X   = "interpolation 2x"
    PenumbraA         = "penumbra a"
    PenumbraB         = "penumbra b"
    PenumbraC         = "penumbra c"
    PenumbraD         = "penumbra d"

    # Darken
    ColorBurn         = "burn"
    LinearBurn        = "linear_burn"
    Darken            = "darken"
    GammaDark         = "gamma_dark"
    DarkerColor       = "darker color"
    ShadeIFSIllusions = "shade_ifs_illusions"
    FogDarkenIFSIllusions = "fog_darken_ifs_illusions"
    EasyBurn          = "easy burn"

    # Lighten
    ColorDodge        = "dodge"
    ColorDodgeHDR     = "dodge_hdr"
    LinearDodge       = "linear_dodge"
    Lighten           = "lighten"
    LinearLight       = "linear light"
    Screen            = "screen"
    PinLight          = "pin_light"
    VividLight        = "vivid_light"
    VividLightHDR     = "vivid_light_hdr"
    FlatLight         = "flat_light"
    HardLight         = "hard_light"
    SoftLightIFSIllusions = "soft_light_ifs_illusions"
    SoftLightPegtopDelphi = "soft_light_pegtop_delphi"
    SoftLightPhotoshop = "soft_light"
    SoftLightSVG      = "soft_light_svg"
    GammaLight        = "gamma_light"
    GammaIllumination = "gamma_illumination"
    LighterColor      = "lighter color"
    PNormA            = "pnorm_a"
    PNormB            = "pnorm_b"
    SuperLight        = "super_light"
    TintIFSIllusions  = "tint_ifs_illusions"
    FogLightenIFSIllusions = "fog_lighten_ifs_illusions"
    EasyDodge         = "easy dodge"
    LuminositySAI     = "luminosity_sai"

    # Misc
    Bumpmap           = "bumpmap"
    CombineNormalMap  = "combine_normal"
    Dissolve          = "dissolve"
    CopyRed           = "copy_red"
    CopyGreen         = "copy_green"
    CopyBlue          = "copy_blue"
    Copy              = "copy"
    TangentNormalmap  = "tangent_normalmap"

    # HSY
    ColorHSY              = "color"
    HueHSY                = "hue"
    TintHSY               = "tint"
    SaturationHSY         = "saturation"
    IncreaseSaturationHSY = "inc_saturation"
    DecreaseSaturationHSY = "dec_saturation"
    LuminosityHSY         = "luminize"
    IncreaseLuminosityHSY = "inc_luminosity"
    DecreaseLuminosityHSY = "dec_luminosity"

    # HSI
    HueHSI                = "hue_hsi"
    ColorHSI              = "color_hsi"
    Saturation_HSI        = "saturation_hsi"
    IncreaseSaturationHSI = "inc_saturation_hsi"
    DecreaseSaturationHSI = "dec_saturation_hsi"
    Intensity             = "intensity"
    Increase_Intensity    = "inc_intensity"
    Decrease_Intensity    = "dec_intensity"

    # HSL
    HueHSL               = "hue_hsl"
    ColorHSL             = "color_hsl"
    SaturationHSL        = "saturation_hsl"
    IncreaseSaturationHSL = "inc_saturation_hsl"
    DecreaseSaturationHSL = "dec_saturation_hsl"
    Lightness             = "lightness"
    IncreaseLightness     = "inc_lightness"
    DecreaseLightness     = "dec_lightness"

    # HSV
    HueHSV                = "hue_hsv"
    ColorHSV              = "color_hsv"
    Saturation_HSV        = "saturation_hsv"
    IncreaseSaturationHSV = "inc_saturation_hsv"
    DecreaseSaturationHSV = "dec_saturation_hsv"
    Value                 = "value"
    IncreaseValue         = "inc_value"
    DecreaseValue         = "dec_value"

    # Quadratic
    Reflect               = "reflect"
    Glow                  = "glow"
    Freeze                = "freeze"
    Heat                  = "heat"
    GlowHeat              = "glow_heat"
    HeatGlow              = "heat_glow"
    ReflectFreeze         = "reflect_freeze"
    FreezeReflect         = "freeze_reflect"
    HeatGlowFreezeReflectHybrid = "heat_glow_freeze_reflect_hybrid"

    # Unknown...
    #IN           = "in"
    #OUT          = "out"
    #PLUS         = "plus"
    #MINUS        = "minus"
    #UNDEF        = "undefined"
    #NO           = "nocomposition"
    #CLEAR        = "clear"
    #PASS_THROUGH = "pass through"
    #COLORIZE     = "colorize"
    #DISPLACE     = "displace"


class TextureBlendingMode(IntEnum): # Non-Pixel-Engine
    Multiply = 0
    Subtract = 1
    Darken = 2
    Overlay = 3
    ColorDodge = 4
    ColorBurn = 5
    LinearDodge = 6
    LinearBurn = 7
    HardMixPhotoshop = 8
    HardMixPhotoshopSofter = 9
    Height = 10
    LinearHeight = 11
    HeightPhotoshop = 12
    LinearHeightPhotoshop = 13

class MaskingBlendingMode(StrEnum):
    Multiply = BlendingMode.Multiply
    Darken = BlendingMode.Darken
    Overlay = BlendingMode.Overlay
    ColorDodge = BlendingMode.ColorDodge
    ColorBurn = BlendingMode.ColorBurn
    LinearBurn = BlendingMode.LinearBurn
    LinearDodge = BlendingMode.LinearDodge
    HardMixPhotoshop = BlendingMode.HardMixPhotoshop
    HardMixSofterPhotoshop = BlendingMode.HardMixSofterPhotoshop
    Subtract = BlendingMode.Subtract

class CurveMode(IntEnum):
    Multiply   = 0
    Addition   = 1
    Maximum    = 2
    Minimum    = 3
    Difference = 4

class ColorSource(StrEnum):
    PlainColor    = "plain"
    Gradient      = "gradient"
    UniformRandom = 'uniform_random'
    TotalRandom   = "total_random"
    Pattern       = "pattern"
    PatternLocked = "pattern_locked"

class PaintingMode(IntEnum):
    BuildUp = 1
    Wash    = 2

class BrushDefinition(str):
    # This is an XML string containing
    # PaintopPreset.brushDefinition['Brush']
    # plus the keys either of Auto, Predefined, or Text
    pass

class SensorId(StrEnum):
    Pressure           = "pressure"
    PressureIn         = "pressurein"
    TangentialPressure = "tangentialpressure"
    DrawingAngle       = "drawingangle"
    XTilt              = "xtilt"
    YTilt              = "ytilt"
    TiltDirection      = "ascension"
    TiltElevation      = "declination"
    Rotation           = "rotation"
    FuzzyDab           = "fuzzy"
    FuzzyStroke        = "fuzzystroke"
    Speed              = "speed"
    Fade               = "fade"
    Distance           = "distance"
    Time               = "time"
    Perspective        = "perspective"

    #SensorsList = "sensorslist"

class Sensor(str):
    # For multiple sensors:
    # <params id="sensorslist">
    # <ChildSensor id="opacity">
    #  <curve>0,0;1,1;</curve>
    # </ChildSensor>
    # </params>
    #
    # For just one:
    # <params id="opacity">
    #  <curve>0,0;1,1;</curve>
    # </params>
    pass

    #def __init__(self, inputId, curve):
    #    self.inputId = inputId
    #    self.curve = curve

class DrawingAngleSensor(Sensor):
    pass
    #fanCornersEnabled, fanCornersStep, angleOffset, lockedAngleMode
class FadeSensor(Sensor):
    pass
    #periodic, length
class DistanceSensor(Sensor):
    # <ChildSensor id="distance" length="30" periodic="0"/>
    pass
    #periodic, length
class TimeSensor(Sensor):
    pass
    #periodic, duration

class Curve(str):
    # <curve>0,0;1,1;</curve>
    # or
    # <curve>0,0;0.25,0.50,is_corner;0.75,0.75;</curve>
    # etc
    # X and Y range from 0 to 1
    pass

# Any Engine ------------------------------------------------------------------
class PaintopPreset():

    def __init__(self):

        self.presetKeys = {
            'name': {'type': str},
            'paintopid': {'type': Paintop},
            'embedded_resources': {'type': int}
        }

        self.keys = {
            'paintop': {'type': Paintop}
        }

        self.keys.update({
            "EraserMode": {'type': bool},
            "SavedEraserSize": {'type': float},
            "SavedBrushSize": {'type': float},
            "SavedEraserOpacity": {'type': float},
            "SavedBrushOpacity": {'type': float},
            "lodUserAllowed": {'type': bool},
            "lodSizeThreshold": {'type': float}
        })

    # Brush Definition is special...
    brushDefinition = { # 'brush_definition'
        'Brush': {
            'type': {'type': BrushTipType},
            'BrushVersion': {'type': int} # 2
        },
        'auto_brush': { #BrushTipType.Auto: {
            #'shape': {'type': AutoBrushTipShape},
            #'type': {'type': AutoBrushTipMaskType},
            #'antialiasEdges': {'type': bool},

            #'diameter': {'type': float},
            #'ratio': {'type': float},
            #'hFade': {'type': float},
            #'vFade': {'type': float},
            'angle': {'type': float}, # stored in radians
            #'spikes': {'type': int},
            'randomness': {'type': int},
            'density': {'type': int},

            'useAutoSpacing': {'type': bool},
            'spacing': {'type': float},
            'autoSpacingCoeff': {'type': float} # ?
        },
        'MaskGenerator': { # for Auto...
            'id': {'type': AutoBrushGenShape},
            'type': {'type': AutoBrushGenType},
            'antialiasEdges': {'type': bool},

            'diameter': {'type': float},
            'ratio': {'type': float},
            'hFade': {'type': float},
            'vFade': {'type': float},
            #'angle': {'type': float},
            'spikes': {'type': int},
            #'randomness': {'type': int},
            #'density': {'type': int},

            # if type == 'soft'
            'softnessCurve': {'type': Curve},
        },
        'png_brush': { #BrushTipType.Predefined: {
            'filename': {'type': str},
            'md5sum': {'type': str},

            'scale': {'type': float},
            'angle': {'type': float}, # stored in radians

            'useAutoSpacing': {'type': bool},
            'spacing': {'type': float},
            'autoSpacingCoeff': {'type': float}, # ?

            'brushApplication': {'type': PredefinedBrushTipMode},
                'ColorAsMask': {'type': int}, # legacy, use brushApplication
            
            'AdjustmentMidPoint': {'type': int},
            'BrightnessAdjustment': {'type': float},
            'ContrastAdjustment': {'type': float},
            'AutoAdjustMidPoint': {'type': int},
            'AdjustmentVersion': {'type': int} # 2
        },
        'kis_text_brush': { #BrushTipType.Text: {
            'font': {'type': str},
            'text': {'type': str}, # See QFont::toString()
            'spacing': {'type': float},
            'pipe': {'type': bool},
        }
    }

    generalParams = {
        'Texture/Pattern': {
            'Texture/Pattern/Enabled': {'type': bool},

            'Texture/Pattern/PatternFileName': {'type': str},
            'Texture/Pattern/Name': {'type': str},
            'Texture/Pattern/PatternMD5Sum': {'type': str},
            'Texture/Pattern/PatternMD5': {'type': str},

            'Texture/Pattern/TexturingMode': {'type': TextureBlendingMode},
            'Texture/Pattern/UseSoftTexturing': {'type': bool},
            'Texture/Pattern/Scale': {'type': float}, # range: 0-20
            'Texture/Pattern/Brightness': {'type': float},
            'Texture/Pattern/Contrast': {'type': float},
            "Texture/Pattern/NeutralPoint": {'type': float},
            'Texture/Pattern/CutoffPolicy': {'type': int},
            'Texture/Pattern/CutoffLeft': {'type': int},
            'Texture/Pattern/CutoffRight': {'type': int},
            'Texture/Pattern/OffsetX': {'type': int},
            'Texture/Pattern/OffsetY': {'type': int},
            'Texture/Pattern/MaximumOffsetX': {'type': int},
            'Texture/Pattern/MaximumOffsetY': {'type': int},
            'Texture/Pattern/isRandomOffsetX': {'type': bool},
            'Texture/Pattern/isRandomOffsetY': {'type': bool},
            'Texture/Pattern/Invert': {'type': bool},
            'Texture/Pattern/AutoInvertOnErase': {'type': bool},
        },
        'KisPrecisionOption': {
            'KisPrecisionOption/precisionLevel': {'type': int},
            'KisPrecisionOption/AutoPrecisionEnabled': {'type': int},
            'KisPrecisionOption/DeltaValue': {'type': int},
            'KisPrecisionOption/SizeToStartFrom': {'type': int}
        }
    }

    def keysForStandardCurveOption(self, option):
        return {
            f"Pressure{option}": {'type': bool},
            f"{option}Sensor": {'type': Sensor},
            f"{option}UseCurve": {'type': bool},
            f"{option}UseSameCurve": {'type': bool},
            f"{option}Value": {'type': float}, # percent stored as decimal
            f"{option}commonCurve": {'type': str},
            f"{option}UseCurve": {'type': CurveMode}
        }


# Pixel Engine ----------------------------------------------------------------
class TextureBlendingModePixelEngine(IntEnum):
    Multiply = 0
    Subtract = 1
    LightnessMap = 2 # Pixel Engine Only
    GradientMap = 3 # Pixel Engine Only
    Darken = 4
    Overlay = 5
    ColorDodge = 6
    ColorBurn = 7
    LinearDodge = 8
    LinearBurn = 9
    HardMixPhotoshop = 10
    HardMixSofterPhotoshop = 11
    Height = 12
    LinearHeight = 13
    HeightPhotoshop = 14
    LinearHeightPhotoshop = 15

class PixelEnginePreset(PaintopPreset):

    def __init__(self):
        super().__init__()

        self.presetKeys['paintopid']['value'] = Paintop.Pixel
        self.keys['paintop']['value'] = Paintop.Pixel

        # > General

        # Brush Tip
        self.keys.update({
            'brush_definition': {'type': BrushDefinition}, # XML string
        })
        self.keys.update(self.generalParams[
            'KisPrecisionOption'
        ])

        # Blending Mode
        self.keys.update({
            'CompositeOp': {'type': BlendingMode}
        })

        # Opacity
        self.keys.update(self.keysForStandardCurveOption(
            'Opacity'
        ))

        # Flow
        self.keys.update(self.keysForStandardCurveOption(
            'Flow'
        ))

        # Size
        self.keys.update(self.keysForStandardCurveOption(
            'Size'
        ))

        # Ratio
        self.keys.update(self.keysForStandardCurveOption(
            'Ratio'
        ))

        # Spacing
        self.keys.update(self.keysForStandardCurveOption(
            'Spacing')|{
            'Spacing/Isotropic': {'type': bool},
            'PaintOpSettings/updateSpacingBetweenDabs': {'type': bool}
        })

        # Mirror
        self.keys.update(self.keysForStandardCurveOption(
            'Mirror')|{
            'HorizontalMirrorEnabled': {'type': bool},
            'VerticalMirrorEnabled': {'type': bool}
        })

        # Softness
        self.keys.update(self.keysForStandardCurveOption(
            'Softness'
        ))

        # Rotation
        self.keys.update(self.keysForStandardCurveOption(
            'Rotation'
        ))

        # Sharpness
        self.keys.update(self.keysForStandardCurveOption(
            'Sharpness')|{
            'Sharpness/factor': {'type': float},
            'Sharpness/alignoutline': {'type': bool},
            'Sharpness/softness': {'type': int}

        })

        # Lightness Strength
        self.keys.update(self.keysForStandardCurveOption(
            'LightnessStrength'
        ))

        # Scatter
        self.keys.update(self.keysForStandardCurveOption(
            'Scatter')|{
            'Scattering/AxisX': {'type': bool},
            'Scattering/AxisY': {'type': bool},
            'Scattering/Amount': {'type': float}
        })

        # > Color
        # Source
        self.keys.update({
            'ColorSource/Type': {'type': ColorSource}
        })

        # Darken
        self.keys.update(self.keysForStandardCurveOption(
            'Darken'
        ))

        # Mix
        self.keys.update(self.keysForStandardCurveOption(
            'Mix'
        ))

        # Hue
        self.keys.update(self.keysForStandardCurveOption(
            'h' # Hue
        ))

        # Saturation
        self.keys.update(self.keysForStandardCurveOption(
            's' # Saturation
        ))

        # Value
        self.keys.update(self.keysForStandardCurveOption(
            'v' # Value
        ))

        # Airbrush
        self.keys.update({
            'PaintOpSettings/isAirbrushing': {'type': bool},
            'PaintOpSettings/rate': {'type': int},
            'PaintOpSettings/ignoreSpacing': {'type': bool} # override spacing
        })

        # Rate
        self.keys.update(self.keysForStandardCurveOption(
            'Rate'
        ))

        # Painting Mode
        self.keys.update({
            'PaintOpAction': {'type': PaintingMode}
        })

        # > Texture
        # Pattern
        self.keys.update(self.generalParams[
            'Texture/Pattern'
        ])
        # override blending mode type
        self.keys['Texture/Pattern/TexturingMode']['type'] = TextureBlendingModePixelEngine

        # Strength
        self.keys.update(self.keysForStandardCurveOption(
            'Texture/Strength/'
        ))

        # > Masked Brush

        self.keys.update({
            'MaskingBrush/Enabled': {'type': bool},
            'MaskingBrush/MasterSizeCoeff': {'type': float},
            'MaskingBrush/UseMasterSize': {'type': bool},
        })
        
        # Brush Tip [Masked]
        self.keys.update({
            'MaskingBrush/MaskingCompositeOp': {'type': MaskingBlendingMode},
            'MaskingBrush/Preset/brush_definition': {'type': BrushDefinition},
        })

        # Opacity [Masked]
        self.keys.update(self.keysForStandardCurveOption(
            'MaskingBrush/Preset/Opacity'
        ))

        # Flow [Masked]
        self.keys.update(self.keysForStandardCurveOption(
            'MaskingBrush/Preset/Flow'
        ))

        # Size [Masked]
        self.keys.update(self.keysForStandardCurveOption(
            'MaskingBrush/Preset/Size'
        ))

        # Ratio [Masked]
        self.keys.update(self.keysForStandardCurveOption(
            'MaskingBrush/Preset/Ratio'
        ))

        # Rotation [Masked]
        self.keys.update(self.keysForStandardCurveOption(
            'MaskingBrush/Preset/Rotation'
        ))

        # Mirror [Masked]
        self.keys.update(self.keysForStandardCurveOption(
            'MaskingBrush/Preset/Mirror')|{
            'MaskingBrush/Preset/HorizontalMirrorEnabled': {'type': bool},
            'MaskingBrush/Preset/VerticalMirrorEnabled': {'type': bool}
        })

        # Scatter [Masked]
        self.keys.update(self.keysForStandardCurveOption(
            'MaskingBrush/Preset/Scatter')|{
            'MaskingBrush/Preset/Scattering/AxisX': {'type': bool},
            'MaskingBrush/Preset/Scattering/AxisY': {'type': bool},
            'MaskingBrush/Preset/Scattering/Amount': {'type': float}
        })



# Color Smudge Engine ---------------------------------------------------------
class SmudgeMode(IntEnum):
    Smearing = 0
    Dulling = 1

class ThicknessMode(IntEnum):
        #RESERVED = 0
        Overwrite = 1
        Overlay = 2

class ColorSmudgeEnginePreset(PaintopPreset):
    def __init__(self):
        super().__init__()

        self.presetKeys['paintopid']['value'] = Paintop.ColorSmudge
        self.keys['paintop']['value'] = Paintop.ColorSmudge

        # > General

        # Brush Tip
        self.keys.update({
            'brush_definition': {'type': BrushDefinition} # XML string
        })
        self.keys.update(self.generalParams[
            'KisPrecisionOption'
        ])


        # Blending Mode
        self.keys.update({
            'CompositeOp': {'type': BlendingMode}
        })

        # Opacity
        self.keys.update(self.keysForStandardCurveOption(
            'Opacity'
        ))

        # Size
        self.keys.update(self.keysForStandardCurveOption(
            'Size'
        ))

        # Ratio
        self.keys.update(self.keysForStandardCurveOption(
            'Ratio'
        ))

        # Spacing
        self.keys.update(self.keysForStandardCurveOption(
            'Spacing')|{
            'Spacing/Isotropic': {'type': bool},
            'PaintOpSettings/updateSpacingBetweenDabs': {'type': bool}
        })

        # Mirror
        self.keys.update(self.keysForStandardCurveOption(
            'Mirror')|{
            'HorizontalMirrorEnabled': {'type': bool},
            'VerticalMirrorEnabled': {'type': bool}
        })

        # Smudge Length
        self.keys.update(self.keysForStandardCurveOption(
            'SmudgeRate')|{
            'SmudgeRateMode': {'type': SmudgeMode},
            'SmudgeRateSmearAlpha': {'type': bool},
            'SmudgeRateUseNewEngine': {'type': bool}
        })

        # Smudge Radius
        self.keys.update(self.keysForStandardCurveOption(
            'SmudgeRadius')|{
            'SmudgeRadiusVersion': {'type': int} # 2
        })

        # Color Rate
        self.keys.update(self.keysForStandardCurveOption(
            'ColorRate')|{
        })

        # Paint Thickness
        self.keys.update(self.keysForStandardCurveOption(
            'PaintThickness')|{
            'PaintThicknessThicknessMode': {'type': ThicknessMode}
        })

        # Rotation
        self.keys.update(self.keysForStandardCurveOption(
            'Rotation'
        ))

        # Scatter
        self.keys.update(self.keysForStandardCurveOption(
            'Scatter')|{
            'Scattering/AxisX': {'type': bool},
            'Scattering/AxisY': {'type': bool},
            'Scattering/Amount': {'type': float}
        })

        # Overlay Mode
        self.keys.update({
            'MergedPaint': {'type': bool}
        })

        # Gradient
        self.keys.update(self.keysForStandardCurveOption(
            'Gradient'
        ))

        # > Color

        # Hue
        self.keys.update(self.keysForStandardCurveOption(
            'h' # Hue
        ))

        # Saturation
        self.keys.update(self.keysForStandardCurveOption(
            's' # Saturation
        ))

        # Value
        self.keys.update(self.keysForStandardCurveOption(
            'v' # Value
        ))

        # Airbrush
        self.keys.update({
            'PaintOpSettings/isAirbrushing': {'type': bool},
            'PaintOpSettings/rate': {'type': int},
            'PaintOpSettings/ignoreSpacing': {'type': bool} # override spacing
        })

        # Rate
        self.keys.update(self.keysForStandardCurveOption(
            'Rate'
        ))

        # Painting Mode
        self.keys.update({
            'PaintOpAction': {'type': PaintingMode}
        })

        # > Texture
        # Pattern
        self.keys.update(self.generalParams[
            'Texture/Pattern'
        ])

        # Strength
        self.keys.update(self.keysForStandardCurveOption(
            'Texture/Strength/'
        ))



# Quick Brush Engine ----------------------------------------------------------
class QuickBrushEnginePreset(PaintopPreset):
    def __init__(self):
        super().__init__()

        self.presetKeys['paintopid']['value'] = Paintop.QuickBrush
        self.keys['paintop']['value'] = Paintop.QuickBrush

        # > General
        # Brush 
        self.key.update({
            'diameter': {'type': float},
            'spacing': {'type': float},
            'useAutoSpacing': {'type': bool},
            'autoSpacingCoeff': {'type': float}
        })

        # Blending Mode
        self.keys.update({
            'CompositeOp': {'type': BlendingMode}
        })

        # Size
        self.keys.update(self.keysForStandardCurveOption(
            'Size'
        ))

        # Spacing
        self.keys.update(self.keysForStandardCurveOption(
            'Spacing')|{
            'Spacing/Isotropic': {'type': bool},
            'PaintOpSettings/updateSpacingBetweenDabs': {'type': bool}
        })



# Sketch Engine ---------------------------------------------------------------
class SketchEnginePreset(PaintopPreset):
    def __init__(self):
        super().__init__()

        self.presetKeys['paintopid']['value'] = Paintop.Sketch
        self.keys['paintop']['value'] = Paintop.Sketch

        # > General
        # Brush Tip
        self.keys.update({
            'brush_definition': {'type': BrushDefinition} # XML string
        })
        self.keys.update(self.generalParams[
            'KisPrecisionOption'
        ])

        # Brush size
        self.keys.update({
            'Sketch/lineWidth': {'type': int},
            'Sketch/offset': {'type': float}, # Offset Scale
            'Sketch/probability': {'type': float}, # Density
            'Sketch/distanceDensity': {'type': bool},
            'Sketch/magnetify': {'type': bool},
            'Sketch/randomRGB': {'type': bool},
            'Sketch/randomOpacity': {'type': bool},
            'Sketch/distanceOpacity': {'type': bool},
            'Sketch/simpleMode': {'type': bool},
            'Sketch/makeConnection': {'type': bool}, # Paint Connection Lines
            'Sketch/antiAliasing': {'type': bool}
        })

        # Blending Mode
        self.keys.update({
            'CompositeOp': {'type': BlendingMode}
        })

        # Opacity
        self.keys.update(self.keysForStandardCurveOption(
            'Opacity'
        ))

        # Size
        self.keys.update(self.keysForStandardCurveOption(
            'Size'
        ))

        # Rotation
        self.keys.update(self.keysForStandardCurveOption(
            'Rotation'
        ))


        # Line width
        self.keys.update(self.keysForStandardCurveOption(
            'Line width'
        ))

        # Offset scale
        self.keys.update(self.keysForStandardCurveOption(
            'Offset scale'
        ))

        # Density
        self.keys.update(self.keysForStandardCurveOption(
            'Density'
        ))

        # > Color

        # Airbrush
        self.keys.update({
            'PaintOpSettings/isAirbrushing': {'type': bool},
            'PaintOpSettings/rate': {'type': int}
        })

        # Rate
        self.keys.update(self.keysForStandardCurveOption(
            'Rate'
        ))

        # Painting Mode
        self.keys.update({
            'PaintOpAction': {'type': PaintingMode}
        })


# Bristle Engine --------------------------------------------------------------
class BristleEnginePreset(PaintopPreset):
    def __init__(self):
        super().__init__()

        self.presetKeys['paintopid']['value'] = Paintop.Bristle
        self.keys['paintop']['value'] = Paintop.Bristle

        # > General

        # Brush Tip
        self.keys.update({
            'brush_definition': {'type': BrushDefinition} # XML string
        })

        # Bristle options
        self.keys.update({
            'HairyBristle/scale': {'type': float},
            'HairyBristle/random': {'type': float}, # Random offset
            'HairyBristle/shear': {'type': float},
            'HairyBristle/density': {'type': float},
            'HairyBristle/useMousePressure': {'type': bool}, # Mouse pressure
            'HairyBristle/threshold': {'type': bool},
            'HairyBristle/isConnected': {'type': bool}, # Connect hairs
            'HairyBristle/antialias': {'type': bool},
            'HairyBristle/useCompositing': {'type': bool}, # Composite bristles
        })

        # > Color
        # Ink depletion
        self.keys.update({
            'HairyInk/enabled': {'type': bool},

            'HairyInk/inkDepletionCurve': {'type': Curve},
            'HairyInk/useWeights': {'type': bool},
            'HairyInk/pressureWeights': {'type', int},
            'HairyInk/bristleInkAmountWeight': {'type': int},
            'HairyInk/bristleLengthWeights': {'type': int},
            'HairyInk/inkDepletionWeight': {'type': int},

            'HairyInk/inkAmount': {'type': int},
            'HairyInk/useOpacity': {'type': bool},
            'HairyInk/useSaturation': {'type': bool},
            'HairyInk/soak': {'type': bool} # Soak ink

        })

        # Blending Mode
        self.keys.update({
            'CompositeOp': {'type': BlendingMode}
        })

        # Opacity
        self.keys.update(self.keysForStandardCurveOption(
            'Opacity'
        ))

        # Size
        self.keys.update(self.keysForStandardCurveOption(
            'Size'
        ))

        # Rotation
        self.keys.update(self.keysForStandardCurveOption(
            'Rotation'
        ))

        # Painting Mode
        self.keys.update({
            'PaintOpAction': {'type': PaintingMode}
        })

# Shape Engine ----------------------------------------------------------------
class ShapeFillStyle(IntEnum):
    SolidColor = 0
    Pattern = 1

class ShapeEnginePreset(PaintopPreset):
    def __init__(self):
        super().__init__()

        self.presetKeys['paintopid']['value'] = Paintop.Shape
        self.keys['paintop']['value'] = Paintop.Shape

        # > General
        # Experiment Option
        self.keys.update({
            'Experiment/speedEnabled': {'type': bool},
            'Experiment/speed': {'type': float},
            'Experiment/smoothing': {'type': bool}, # Smooth
            'Experiment/smoothingValue': {'type': float},
            'Experiment/displacementEnabled': {'type': bool},
            'Experiment/displacement': {'type': float},
            'Experiment/windingFill': {'type': bool},
            'Experiment/hardEdge': {'type': bool},
            'Experiment/fillType': {'type': ShapeFillStyle}
        })

        # Blending Mode
        self.keys.update({
            'CompositeOp': {'type': BlendingMode}
        })


# Spray Engine ----------------------------------------------------------------
class SprayParticleDistribution(IntEnum):
    Uniform = 0
    Gaussian = 1 # Radial only
    ClusterBased = 2 # Radial only
    CurveBased = 3

class SprayShape(IntEnum):
    Ellipse = 0
    Rectangle = 1
    AntiAliasedPixel = 2
    Pixel = 3
    Image = 4

class SprayEnginePreset(PaintopPreset):
    def __init__(self):
        super().__init__()

        self.presetKeys['paintopid']['value'] = Paintop.Spray
        self.keys['paintop']['value'] = Paintop.Spray

        # > General
        # Spray Area
        self.keys.update({
            # Area
            'Spray/diameter': {'type': int},
            'Spray/aspect': {'type': float},
            'Spray/rotation': {'type': float},
            'Spray/scale': {'type': float},
            'Spray/spacing': {'type': float},
            'Spray/jitterMovement': {'type': bool},
            'Spray/jitterMoveAmount': {'type': float},
            # Particles
            'Spray/useDensity': {'type': bool}, # false=Count, true=Density
            'Spray/particleCount': {'type': int}, # Count
            'Spray/coverage': {'type': float}, # Density
            'Spray/angularDistributionType': {'type': SprayParticleDistribution}, # 0 or 3 only
            'Spray/angularDistributionCurve': {'type': Curve}, # Curve
            'Spray/angularDistributionCurveRepeat': {'type': int}, # Curve
            'Spray/radialDistributionType': {'type': SprayParticleDistribution},
                'Spray/gaussianDistribution': {'type': bool}, # legacy, use radialDistributionType
            'Spray/radialDistributionStdDeviation': {'type': float}, # Gaussian
            'Spray/radialDistributionClusteringAmount': {'type': float}, # Cluster
            'Spray/radialDistributionCurve': {'type': Curve}, # Curve
            'Spray/radialDistributionCurveRepeat': {'type': int}, # Curve
            'Spray/radialDistributionCenterBiased': {'type': bool} # Uniform or Gaussian
        })

        # Spray Shape
        self.keys.update({
            'SprayShape/enabled': {'type': bool},
            'SprayShape/shape': {'type': SprayShape},
            'SprayShape/width': {'type': int},
            'SprayShape/height': {'type': int},
            'SprayShape/proportional': {'type': bool},
            'SprayShape/imageUrl': {'type': str} # Texture
        })

        # Brush Tip
        self.keys.update({
            'brush_definition': {'type': BrushDefinition} # XML string
        })
        self.keys.update(self.generalParams[
            'KisPrecisionOption'
        ])

        # Opacity
        self.keys.update(self.keysForStandardCurveOption(
            'Opacity'
        ))

        # Size
        self.keys.update(self.keysForStandardCurveOption(
            'Size'
        ))

        # Blending Mode
        self.keys.update({
            'CompositeOp': {'type': BlendingMode}
        })

        # Shape dynamics
        self.keys.update({
            'ShapeDynamicsVersion': {'type': int}, # old brushes have "SprayShape" instead

            'ShapeDynamics/enabled': {'type': bool},

            'ShapeDynamics/randomSize': {'type': bool},

            'ShapeDynamics/fixedRotation': {'type': bool},
            'ShapeDynamics/fixedAngle': {'type': int},
            'ShapeDynamics/randomRotation': {'type': bool},
            'ShapeDynamics/randomRotationWeight': {'type': float},
            'ShapeDynamics/followCursor': {'type': bool},
            'ShapeDynamics/followCursorWeigth': {'type': float}, # [sic]
            'ShapeDynamics/followDrawingAngle': {'type': bool},
            'ShapeDynamics/followDrawingAngleWeigth': {'type': float}, # [sic]
        })

        # > Color

        # Color options
        self.keys.update({
            'ColorOption/useRandomHSV': {'type': bool},
            'ColorOption/hue': {'type': int},
            'ColorOption/saturation': {'type': int},
            'ColorOption/value': {'type': int},
            'ColorOption/useRandomOpacity': {'type': bool},
            'ColorOption/colorPerParticle': {'type': bool},
            'ColorOption/sampleInputColor': {'type': bool},
            'ColorOption/fillBackground': {'type': bool},
            'ColorOption/mixBgColor': {'type': bool}
        })

        # Rotation
        self.keys.update(self.keysForStandardCurveOption(
            'Rotation'
        ))

        # Airbrush
        self.keys.update({
            'PaintOpSettings/isAirbrushing': {'type': bool},
            'PaintOpSettings/rate': {'type': int},
            'PaintOpSettings/ignoreSpacing': {'type': bool} # override spacing
        })

        # Rate
        self.keys.update(self.keysForStandardCurveOption(
            'Rate'
        ))

        # Painting Mode
        self.keys.update({
            'PaintOpAction': {'type': PaintingMode}
        })


# Hatching Engine -------------------------------------------------------------
class HatchingEnginePreset(PaintopPreset):
    def __init__(self):
        super().__init__()

        self.presetKeys['paintopid']['value'] = Paintop.Hatching
        self.keys['paintop']['value'] = Paintop.Hatching

        # > General
        # Brush Tip
        self.keys.update({
            'brush_definition': {'type': BrushDefinition} # XML string
        })
        self.keys.update(self.generalParams[
            'KisPrecisionOption'
        ])

        # Hatching options
        self.keys.update({
            'Hatching/angle': {'type': float},
            'Hatching/separation': {'type': float},
            'Hatching/thickness': {'type': float},
            'Hatching/origin_x': {'type': float},
            'Hatching/origin_y': {'type': float},

            # mutually exclusive
            'Hatching/bool_nocrosshatching': {'type': bool},
            'Hatching/bool_perpendicular': {'type': bool},
            'Hatching/bool_minusthenplus': {'type': bool},
            'Hatching/bool_plusthenminus': {'type': bool},
            'Hatching/bool_moirepattern': {'type': bool},

            'Hatching/separationintervals': {'type': int}
        })

        # Hatching preferences
        self.keys.update({
            'Hatching/bool_antialias': {'type': bool},
            'Hatching/bool_subpixelprecision': {'type': bool},
            'Hatching/bool_opaquebackground': {'type': bool} # Color background
        })

        # Blending Mode
        self.keys.update({
            'CompositeOp': {'type': BlendingMode}
        })

        # Separation
        self.keys.update(self.keysForStandardCurveOption(
            'Separation'
        ))

        # Thickness
        self.keys.update(self.keysForStandardCurveOption(
            'Thickness'
        ))

        # Angle
        self.keys.update(self.keysForStandardCurveOption(
            'Angle'
        ))

        # Crosshatching
        self.keys.update(self.keysForStandardCurveOption(
            'Crosshatching'
        ))

        # Opacity
        self.keys.update(self.keysForStandardCurveOption(
            'Opacity'
        ))

        # Size
        self.keys.update(self.keysForStandardCurveOption(
            'Size'
        ))

        # Mirror
        self.keys.update(self.keysForStandardCurveOption(
            'Mirror')|{
            'HorizontalMirrorEnabled': {'type': bool},
            'VerticalMirrorEnabled': {'type': bool}
        })

        # > Color 
        # Painting Mode
        self.keys.update({
            'PaintOpAction': {'type': PaintingMode}
        })

        # > Texture
        # Pattern
        self.keys.update(self.generalParams[
            'Texture/Pattern'
        ])

        # Strength
        self.keys.update(self.keysForStandardCurveOption(
            'Texture/Strength/'
        ))


# Grid Engine -----------------------------------------------------------------
class GridShape(IntEnum):
    Ellipse = 0
    Rectangle = 1
    Line = 2
    Pixel = 3
    AntiAliasedPixel = 4

class GridEnginePreset(PaintopPreset):
    def __init__(self):
        super().__init__()

        self.presetKeys['paintopid']['value'] = Paintop.Grid
        self.keys['paintop']['value'] = Paintop.Grid

        # > General
        # Brush size
        self.keys.update({
            'Grid/diameter': {'type': int},
            'Grid/gridWidth': {'type': int},
            'Grid/gridHeight': {'type': int},
            'Grid/horizontalOffset': {'type': float},
            'Grid/verticalOffset': {'type': float},
            'Grid/divisionLevel': {'type': int},
            'Grid/pressureDivision': {'type': bool}, # Division by pressure
            'Grid/scale': {'type': float},
            'Grid/verticalBorder': {'type': float},
            'Grid/horizontalBorder': {'type': float},
            'Grid/randomBorder': {'type': bool} # Jitter borders
        })

        # Particle type
        self.keys.update({
            'GridShape/shape': {'type': GridShape}
        })

        # Blending Mode
        self.keys.update({
            'CompositeOp': {'type': BlendingMode}
        })

        # > Color
        # Color options
        self.keys.update({
            'ColorOption/useRandomHSV': {'type': bool},
            'ColorOption/hue': {'type': int},
            'ColorOption/saturation': {'type': int},
            'ColorOption/value': {'type': int},
            'ColorOption/useRandomOpacity': {'type': bool},
            'ColorOption/colorPerParticle': {'type': bool},
            'ColorOption/sampleInputColor': {'type': bool},
            'ColorOption/fillBackground': {'type': bool},
            'ColorOption/mixBgColor': {'type': bool}
        })

        # Painting Mode
        self.keys.update({
            'PaintOpAction': {'type': PaintingMode}
        })


# Curve Engine ----------------------------------------------------------------
class CurveEnginePreset(PaintopPreset):
    def __init__(self):
        super().__init__()

        self.presetKeys['paintopid']['value'] = Paintop.Curve
        self.keys['paintop']['value'] = Paintop.Curve

        # > General

        # Value
        self.keys.update({
            'Curve/lineWidth': {'type': int},
            'Curve/strokeHistorySize': {'type': int},
            'Curve/curvesOpacity': {'type': float},
            'Curve/makeConnection': {'type': bool},
            'Curve/smoothing': {'type': bool}
        })

        # Opacity
        self.keys.update(self.keysForStandardCurveOption(
            'Opacity'
        ))

        # Line width
        self.keys.update(self.keysForStandardCurveOption(
            'Line width'
        ))

        # Curves opacity
        self.keys.update(self.keysForStandardCurveOption(
            'Curves opacity'
        ))

        # Blending Mode
        self.keys.update({
            'CompositeOp': {'type': BlendingMode}
        })

        # > Color
        # Painting Mode
        self.keys.update({
            'PaintOpAction': {'type': PaintingMode}
        })

# Particle Engine -------------------------------------------------------------
class ParticleEnginePreset(PaintopPreset):
    def __init__(self):
        super().__init__()

        self.presetKeys['paintopid']['value'] = Paintop.Particle
        self.keys['paintop']['value'] = Paintop.Particle

        #Brush Size
        self.keys.update({
            # Particles 
            'Particle/count': {'type': int},
            # Opacity weight
            'Particle/weight': {'type': float},
            # dx scale 
            'Particle/scaleX': {'type': float},
            # dy scale 
            'Particle/scaleY': {'type': float},
            # Gravity 
            'Particle/gravity': {'type': float},
            # Iterations
            'Particle/iterations': {'type': int}
        })

        # Blending Mode
        self.keys.update({
            'CompositeOp': {'type': BlendingMode}
        })

        # > Color

        # Airbrush
        self.keys.update({
            'PaintOpSettings/isAirbrushing': {'type': bool},
            'PaintOpSettings/rate': {'type': int},
        })

        # Rate
        self.keys.update(self.keysForStandardCurveOption(
            'Rate'
        ))

        # Painting Mode
        self.keys.update({
            'PaintOpAction': {'type': PaintingMode}
        })


# Clone Engine ----------------------------------------------------------------
class CloneEnginePreset(PaintopPreset):
    def __init__(self):
        super().__init__()

        self.presetKeys['paintopid']['value'] = Paintop.Clone
        self.keys['paintop']['value'] = Paintop.Clone

        # Brush Tip
        self.keys.update({
            'brush_definition': {'type': BrushDefinition} # XML string
        })
        self.keys.update(self.generalParams[
            'KisPrecisionOption'
        ])

        # Blending Mode
        self.keys.update({
            'CompositeOp': {'type': BlendingMode}
        })

        # Opacity
        self.keys.update(self.keysForStandardCurveOption(
            'Opacity'
        ))

        # Size
        self.keys.update(self.keysForStandardCurveOption(
            'Size'
        ))

        # Rotation
        self.keys.update(self.keysForStandardCurveOption(
            'Rotation'
        ))

        # Mirror
        self.keys.update(self.keysForStandardCurveOption(
            'Mirror')|{
            'HorizontalMirrorEnabled': {'type': bool},
            'VerticalMirrorEnabled': {'type': bool}
        })

        # > Color
        # Painting Mode
        self.keys.update({
            # Healing
            'Duplicateop/Healing': {'type': bool},
            # Source point move
            'Duplicateop/MoveSourcePoint': {'type': bool},
            # Source point reset before a new stroke
            'Duplicateop/ResetSourcePoint': {'type': bool},
            # Clone From All Visible Layers
            'Duplicateop/CloneFromProjection': {'type': bool},

            'Duplicateop/CorrectPerspective': {'type': bool} # ???
        })

        # > Texture
        # Pattern
        self.keys.update(self.generalParams[
            'Texture/Pattern'
        ])

        # Strength
        self.keys.update(self.keysForStandardCurveOption(
            'Texture/Strength/'
        ))

# Deform Engine ---------------------------------------------------------------
class DeformMode(IntEnum):
    Grow = 1
    Shrink = 2
    SwirlCW = 3
    SwirlCCW = 4
    Move = 5
    LensIn = 6
    LensOut = 7
    DeformColor = 8
class DeformEnginePreset(PaintopPreset):
    def __init__(self):
        super().__init__()

        self.presetKeys['paintopid']['value'] = Paintop.Deform
        self.keys['paintop']['value'] = Paintop.Deform

        # > General
        # Brush size
        self.keys.update({
            #'Brush/shape': {'type': DeformShape}, # always Ellipse, not used
            'Brush/diameter': {'type': float},
            'Brush/aspect': {'type': float},
            'Brush/scale': {'type': float},
            'Brush/rotation': {'type': float},
            'Brush/spacing': {'type': float},
            'Brush/density': {'type': float},
            'Brush/jitterMovement': {'type': float},
            'Brush/jitterMovementEnabled': {'type': bool}
        })
        # Deform Options
        self.keys.update({
            'Deform/deformAction': {'type': DeformMode},
            'Deform/deformAmount': {'type': float},
            'Deform/bilinear': {'type': bool},
            'Deform/useCounter': {'type': bool},
            'Deform/useOldData': {'type': bool} # Use undeformed image
        })

        # Blending Mode
        self.keys.update({
            'CompositeOp': {'type': BlendingMode}
        })

        # Opacity
        self.keys.update(self.keysForStandardCurveOption(
            'Opacity'
        ))

        # Size
        self.keys.update(self.keysForStandardCurveOption(
            'Size'
        ))

        # Rotation
        self.keys.update(self.keysForStandardCurveOption(
            'Rotation'
        ))

        # Airbrush
        self.keys.update({
            'PaintOpSettings/isAirbrushing': {'type': bool},
            'PaintOpSettings/rate': {'type': int},
            'PaintOpSettings/ignoreSpacing': {'type': bool} # override spacing
        })
        # Rate
        self.keys.update(self.keysForStandardCurveOption(
            'Rate'
        ))


# Tangent Normal Engine -------------------------------------------------------
class TangentTiltAxis(IntEnum):
    PositiveX = 0
    NegativeX = 1
    PositiveY = 2
    NegativeY = 3
    PositiveZ = 4
    NegativeZ = 5

class TangentTiltDirectionType(IntEnum):
    Tilt = 0
    Direction = 1
    Rotation = 2
    Mix = 3

class TangentNormalEnginePreset(PaintopPreset):
    def __init__(self):
        super().__init__()

        self.presetKeys['paintopid']['value'] = Paintop.TangentNormal
        self.keys['paintop']['value'] = Paintop.TangentNormal

        # > General

        # Brush Tip
        self.keys.update({
            'brush_definition': {'type': BrushDefinition} # XML string
        })
        self.keys.update(self.generalParams[
            'KisPrecisionOption'
        ])

        # Blending Mode
        self.keys.update({
            'CompositeOp': {'type': BlendingMode}
        })

        # Opacity
        self.keys.update(self.keysForStandardCurveOption(
            'Opacity'
        ))

        # Flow
        self.keys.update(self.keysForStandardCurveOption(
            'Flow'
        ))

        # Size
        self.keys.update(self.keysForStandardCurveOption(
            'Size'
        ))

        # Tangent Tilt
        self.keys.update({
            'Tangent/swizzleRed': {'type': TangentTiltAxis},
            'Tangent/swizzleGreen': {'type': TangentTiltAxis},
            'Tangent/swizzleBlue': {'type': TangentTiltAxis},
            'Tangent/directionType': {'type': TangentTiltDirectionType},
            'Tangent/elevationSensitivity': {'type': float},
            'Tangent/mixValue': {'type': float},
        })

        # Spacing
        self.keys.update(self.keysForStandardCurveOption(
            'Spacing')|{
            'Spacing/Isotropic': {'type': bool},
            'PaintOpSettings/updateSpacingBetweenDabs': {'type': bool}
        })

        # Mirror
        self.keys.update(self.keysForStandardCurveOption(
            'Mirror')|{
            'HorizontalMirrorEnabled': {'type': bool},
            'VerticalMirrorEnabled': {'type': bool}
        })

        # Softness
        self.keys.update(self.keysForStandardCurveOption(
            'Softness'
        ))

        # Sharpness
        self.keys.update(self.keysForStandardCurveOption(
            'Sharpness')|{
            'Sharpness/factor': {'type': float},
            'Sharpness/alignoutline': {'type': bool},
            'Sharpness/softness': {'type': int}

        })

        # Scatter
        self.keys.update(self.keysForStandardCurveOption(
            'Scatter')|{
            'Scattering/AxisX': {'type': bool},
            'Scattering/AxisY': {'type': bool},
            'Scattering/Amount': {'type': float}
        })

        # Rotation
        self.keys.update(self.keysForStandardCurveOption(
            'Rotation'
        ))

        # > Color
        # Airbrush
        self.keys.update({
            'PaintOpSettings/isAirbrushing': {'type': bool},
            'PaintOpSettings/rate': {'type': int},
            'PaintOpSettings/ignoreSpacing': {'type': bool} # override spacing
        })
        # Rate
        self.keys.update(self.keysForStandardCurveOption(
            'Rate'
        ))

        # Painting Mode
        self.keys.update({
            'PaintOpAction': {'type': PaintingMode}
        })

        # > Texture
        # Pattern
        self.keys.update(self.generalParams[
            'Texture/Pattern'
        ])

        # Strength
        self.keys.update(self.keysForStandardCurveOption(
            'Texture/Strength/'
        ))

# Filter Engine ---------------------------------------------------------------
class FilterEnginePreset(PaintopPreset):
    def __init__(self):
        super().__init__()

        self.presetKeys['paintopid']['value'] = Paintop.Filter
        self.keys['paintop']['value'] = Paintop.Filter

        # >General
        # Brush Tip
        self.keys.update({
            'brush_definition': {'type': BrushDefinition} # XML string
        })
        self.keys.update(self.generalParams[
            'KisPrecisionOption'
        ])

        # Blending Mode
        self.keys.update({
            'CompositeOp': {'type': BlendingMode}
        })

        # Opacity
        self.keys.update(self.keysForStandardCurveOption(
            'Opacity'
        ))

        # Size
        self.keys.update(self.keysForStandardCurveOption(
            'Size'
        ))

        # Rotation
        self.keys.update(self.keysForStandardCurveOption(
            'Rotation'
        ))

        # Mirror
        self.keys.update(self.keysForStandardCurveOption(
            'Mirror')|{
            'HorizontalMirrorEnabled': {'type': bool},
            'VerticalMirrorEnabled': {'type': bool}
        })

        # > Color
        # Filter
        self.keys.update({
            'Filter/id': {'type': str}, # Enum
            'Filter/smudgeMode': {'type': bool},
            'Filter/configuration': {'type': str} # Filter configuration string
        })

# MyPaint Engine --------------------------------------------------------------
class MyPaintEnginePreset(PaintopPreset):
    def keysForMyPaintCurveOption(self, option):
        return {
            # ???
            self.keysForStandardCurveOption(option)
        }

    def __init__(self):
        super().__init__()

        self.presetKeys['paintopid']['value'] = Paintop.MyPaint
        self.keys['paintop']['value'] = Paintop.MyPaint

        # 'MyPaint/json': {'type': bytes}

        # > General

        # Basic
            # radius log
            # hardness
            # opacity
        self.keys.update({
            'EraserMode': {'type': bool}
        })

        # > Basic
        # Radius Logarithmic
        self.keys.update({self.keysForMyPaintCurveOption(
            'radius_logarithmic'
        )})
        # Radius by Random
        self.keys.update({self.keysForMyPaintCurveOption(
            'radius_by_random'
        )})
        # Hardness
        self.keys.update({self.keysForMyPaintCurveOption(
            'hardness'
        )})
        # Anti Aliasing
        self.keys.update({self.keysForMyPaintCurveOption(
            'anti_aliasing'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'elliptical_dab_angle'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'elliptical_dab_ratio'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'direction_filter'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'snap_to_pixel'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'pressure_gain_log'
        )})

        # > Airbrush
        self.keys.update({
            'PaintOpSettings/isAirbrushing': {'type': bool},
            'PaintOpSettings/rate': {'type': int},
            'PaintOpSettings/ignoreSpacing': {'type': bool} # override spacing
        })

        # > Color
        self.keys.update({self.keysForMyPaintCurveOption(
            'change_color_h'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'change_color_l'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'change_color_v'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'change_color_hsl_s'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'change_color_hsv_s'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'colorize'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'posterize'
        )})
        # Posterization Levels
        self.keys.update({self.keysForMyPaintCurveOption(
            'posterization_num'
        )})

        # > Speed
        self.keys.update({self.keysForMyPaintCurveOption(
            'speed1_gamma'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'speed2_gamma'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'speed1_slowness'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'speed2_slowness'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'offset_by_speed'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'offset_by_speed_slowness'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'offset_by_random'
        )})

        # > Dabs
        self.keys.update({self.keysForMyPaintCurveOption(
            'dabs_per_basic_radius'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'dabs_per_actual_radius'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'dabs_per_basic_second'
        )})

        # > Opacity
        self.keys.update({self.keysForMyPaintCurveOption(
            'opaque'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'opaque_linearize'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'opaque_multiply'
        )})

        # > Tracking
        self.keys.update({self.keysForMyPaintCurveOption(
            'slow_tracking_per_dab'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'slow_tracking'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'tracking_noise'
        )})

        # > Smudge
        self.keys.update({self.keysForMyPaintCurveOption(
            'smudge'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'smudge_length'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'smudge_length_log'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'smudge_radius_log'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'smudge_transparency'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'smudge_bucket'
        )})

        # > Stroke
        self.keys.update({self.keysForMyPaintCurveOption(
            'stroke_duration_logarithmic'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'stroke_holdtime'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'stroke_threshold'
        )})

        # > Custom
        self.keys.update({self.keysForMyPaintCurveOption(
            'custom_input'
        )})
        self.keys.update({self.keysForMyPaintCurveOption(
            'custom_input_slowness'
        )})
