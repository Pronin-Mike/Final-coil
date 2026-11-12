"""Active compact village layout. Coordinates are centimetres in Unreal world space.

Use this plan for subsequent village edits rather than the original pre-alpha
inventory or legacy house/road generators. terrain_profile.height() reads the
current working collision surface from SourceArt/Terrain/heightfield.json.
"""
import json,os
ROOT='D:/GameDevelop/FinalCoil'
PLAN_PATH=ROOT+'/SourceArt/CompactVillage/plan.json'
def load():
 with open(PLAN_PATH,encoding='utf-8') as f:return json.load(f)
