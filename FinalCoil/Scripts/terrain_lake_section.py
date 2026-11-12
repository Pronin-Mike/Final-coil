import json,sys,math
sys.path.insert(0,"D:/GameDevelop/FinalCoil/Scripts")
import terrain_profile as T
rows=[]
for y in range(110000,243001,250):
    rows.append({"distance_m":(y-110000)/100,"x_cm":62333,"y_cm":y,"ground_m":T.height(62333,y)/100,"water_m":-2.5})
json.dump({"section_x_cm":62333,"samples":rows,"source":"Rendered heightfield triangles; native bed collision spot checks in native_checks.json"},open(T.ROOT+"/Review/TerrainV2/lake_section.json","w"),indent=2)
