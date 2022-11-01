from ..helpers.typing_annotations import ShopApi
from ..helpers.timeseries import remove_consecutive_duplicates
from .shop_api import get_time_resolution, get_attribute_value

def write_pyshop_model_file(file_path:str, shop_api:ShopApi, static_data_only:bool) -> None:

    #Write a pyshop script file to recreate the current input model definition

        with open(file_path,"w",encoding="utf-8") as f:
            #Basic imports
            f.write("from pyshop import ShopSession\n")
            f.write("import pandas as pd\n")
            f.write("from pandas import Timestamp\n")
            f.write("\n")

            #Init ShopSession
            f.write("shop = ShopSession()\n\n")

            #Set time resolution
            time_res = get_time_resolution(shop_api)
            step_length = remove_consecutive_duplicates(time_res['timeresolution'])
            t = list(step_length.index)
            y = list(step_length.values)
            f.write(f"t = {t}\n")
            f.write(f"y = {y}\n")
            f.write(f"step_length = pd.Series(y,index=t)\n")
            f.write(f"shop.set_time_resolution(Timestamp('{time_res['starttime']}'),Timestamp('{time_res['endtime']}'),'{time_res['timeunit']}',step_length)\n")
            f.write("\n")

            all_types = shop_api.GetObjectTypesInSystem()
            all_names = shop_api.GetObjectNamesInSystem()

            #Save the objects in the same order every time
            unique_types = list(set(all_types))
            unique_types.sort(reverse=True)

            #Save a list of all 'active' objects with attributes to write
            objects = []
            for type in unique_types:
                
                #Always skip the scenario object if there is only one of them
                if type == "scenario" and all_types.count("scenario") == 1:
                    continue
                
                attributes = shop_api.GetObjectTypeAttributeNames(type)
                datatypes = shop_api.GetObjectTypeAttributeDatatypes(type)

                input_attributes = []
                input_datatypes = []
                for attr,dtype in zip(attributes,datatypes):
                    
                    #Don't include time dependent data if specified
                    if static_data_only and (dtype == "txy" or dtype == "xyt"):
                        continue

                    #Don't include output attributes
                    if shop_api.GetAttributeInfo(type, attr, "isInput") == "False":
                        continue

                    #Don't include internal attributes
                    if "INTERNAL" in shop_api.GetAttributeInfo(type, attr, "licenseName"):
                        continue

                    input_attributes.append(attr)
                    input_datatypes.append(dtype)

                obj_names = [name for name,obj_type in zip(all_names,all_types) if obj_type==type]

                for i,name in enumerate(obj_names):

                    active_attributes = []
                    active_attribute_names = []
                    active_attribute_datatypes = []
                    for attr,dtype in zip(input_attributes,input_datatypes):
                        
                        #Skip attributes that are default for the object
                        if shop_api.AttributeIsDefault(type,name,attr):
                            continue             

                        val = get_attribute_value(shop_api,name,type,attr,dtype)
                        
                        #Skip attributes that were actually not active
                        if val is None:
                            continue
                        
                        active_attributes.append(val)
                        active_attribute_names.append(attr)
                        active_attribute_datatypes.append(dtype)

                    #Add another active object if there is at least one active input attribute OR the object is an (empty) input object
                    if len(active_attributes) > 0 or shop_api.GetObjectInfo(type,"isInput") == "True":
                        obj = {}
                        obj["type"] = type
                        obj["name"] = name
                        obj["code_name"] = f"{type}_{i+1}"
                        obj["attributes"] = active_attributes
                        obj["attribute_names"] = active_attribute_names
                        obj["attribute_datatypes"] = active_attribute_datatypes                     
                        objects.append(obj)
                        
            #Write the active input attributes of each object to the file
            for obj in objects:
                           
                var_name = obj["code_name"]
                type = obj["type"]
                name = obj["name"]
                
                #Create or retrieve the object depending on if it is an input type or not
                if shop_api.GetObjectInfo(obj["type"],"isInput") == "True":
                    f.write(f"{var_name} = shop.model.{type}.add_object('{name}')\n")
                else:
                    f.write(f"{var_name} = shop.model.{type}['{name}']\n")

                #Set all active attributes
                for val,attr,dtype in zip(obj["attributes"],obj["attribute_names"],obj["attribute_datatypes"]):

                    if dtype == "int" or dtype == "double":
                        f.write(f"{var_name}.{attr}.set({val})\n")
                    elif dtype == "string":
                        f.write(f"{var_name}.{attr}.set('{val}')\n")
                    elif dtype == "int_array" or dtype == "double_array":
                        f.write(f"val_list = {val}\n")
                        f.write(f"{var_name}.{attr}.set(val_list)\n")
                    elif dtype == "string_array":
                        input_list = f"val_list = ['{val[0]}'"
                        for v in val[1:]:
                            input_list += f", '{v}'"
                        input_list += "]\n"
                        f.write(input_list)
                        f.write(f"{var_name}.{attr}.set(val_list)\n")           
                    elif dtype == "sy":
                        f.write(f"s = {list(val.index)}\n")
                        f.write(f"y = {list(val.values)}\n")
                        f.write(f"sy = pd.Series(y,index=s)\n")
                        f.write(f"{var_name}.{attr}.set(sy)\n")                                
                    elif dtype == "xy":
                        f.write(f"x = {list(val.index)}\n")
                        f.write(f"y = {list(val.values)}\n")
                        f.write(f"xy = pd.Series(y,index=x,name={val.name})\n")
                        f.write(f"{var_name}.{attr}.set(xy)\n")    
                    elif dtype == "xy_array":
                        f.write("xy_curves = []\n")
                        for xy in val:
                            f.write(f"x = {list(xy.index)}\n")
                            f.write(f"y = {list(xy.values)}\n")
                            f.write(f"xy = pd.Series(y,index=x,name={xy.name})\n")
                            f.write(f"xy_curves.append(xy)\n")
                        f.write(f"{var_name}.{attr}.set(xy_curves)\n") 
                    elif dtype == "xyt":
                        f.write("xyt = []\n")
                        for xy in val:               
                            f.write(f"x = {list(xy.index)}\n")
                            f.write(f"y = {list(xy.values)}\n")
                            f.write(f"xy = pd.Series(y,index=x,name={xy.name})\n")
                            f.write(f"xyt.append(xy)\n")
                        f.write(f"{var_name}.{attr}.set(xyt)\n")                                                                   
                    elif dtype == "txy":
                        val = remove_consecutive_duplicates(val)
                        if len(val.values) > 1:
                            f.write(f"t = {list(val.index)}\n")
                            f.write(f"y = {list(val.values)}\n")
                            f.write(f"txy = pd.Series(y,index=t)\n")
                            f.write(f"{var_name}.{attr}.set(txy)\n")                                                                   
                        else:
                            f.write(f"{var_name}.{attr}.set({val.values[0]})\n")                                                                   
                
                f.write("\n")

            #Find and write all connections
            connections = []
            connection_types = ["standard","bypass","spill"]
            
            f.write("\n#Connections\n")
            for obj in objects:
                
                up_name = obj["code_name"]
                type = obj["type"]
                name = obj["name"]
                
                wrote_connection = False

                for ctype in connection_types:
                    
                    #Get connected objects for the connection type
                    related_indices = shop_api.GetRelations(type, name, f"connection_{ctype}")
                
                    for i in related_indices:   

                        rel_name = all_names[i]
                        rel_type = all_types[i]

                        #Find the related object in the active object list
                        rel_obj = None
                        for o in objects:
                            if o["name"] == rel_name and o["type"] == rel_type:
                                rel_obj = o
                                break

                        if rel_obj is None:
                            print(f"Object {rel_type} {rel_name} related to {obj} not found!")
                            raise RuntimeError

                        #Check if the connection (or its reverse) has already been added
                        connection_exists = False
                        for c in connections:

                            identical = c["from"] == obj and c["to"] == rel_obj
                            reversed = c["from"] == rel_obj and c["to"] == obj

                            if identical or reversed:
                                connection_exists = True
                                break
                        
                        #Add the connection to the list and write the line to connect the two objects
                        if not connection_exists:                            

                            connections.append({"from":obj,"to":rel_obj,"connection_type":ctype})
                            down_name = rel_obj["code_name"]
                            f.write(f"{up_name}.connect_to({down_name},connection_type='{ctype}')\n")
                            wrote_connection = True
                
                #Add a new line when we are done with an object
                if wrote_connection:
                    f.write("\n")