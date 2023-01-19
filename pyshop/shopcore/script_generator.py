from ..helpers.typing_annotations import ShopApi
from ..helpers.timeseries import remove_consecutive_duplicates
from .shop_api import get_time_resolution, get_attribute_value

import unicodedata

def write_pyshop_model_file(file_path:str, shop_api:ShopApi, static_data_only:bool) -> None:

    #Write a pyshop script file to recreate the current input model definition
    with open(file_path,"w",encoding="utf-8") as f:
        #Basic imports
        f.write("from pyshop import ShopSession\n")
        f.write("import pandas as pd\n")

        #Manually import Timestamp from pandas so that Timestamp objects can be written directly to the file as strings
        f.write("from pandas import Timestamp\n")
        #Manually import nan from numpy so that nan values in TXYs can be written directly to the file as strings
        f.write("from numpy import nan\n")
        f.write("\n")

        #Init ShopSession
        f.write("def get_model() -> ShopSession:\n\n")
        f.write("    #Initialize a new ShopSession\n")
        f.write("    shop = ShopSession()\n\n")

        #Set time resolution
        time_res = get_time_resolution(shop_api)
        f.write("    #Set the time resolution of the optimization\n")
        f.write(f"    start_time = Timestamp('{time_res['starttime']}')\n")
        f.write(f"    end_time = Timestamp('{time_res['endtime']}')\n")
        step_length = remove_consecutive_duplicates(time_res['timeresolution'])
        t = list(step_length.index)
        y = list(step_length.values)
        f.write(f"    t = {t}\n")
        f.write(f"    y = {y}\n")
        f.write(f"    step_length = pd.Series(y,index=t)\n")
        f.write(f"    shop.set_time_resolution(start_time, end_time, '{time_res['timeunit']}', step_length)\n")
        f.write("\n")

        all_types = shop_api.GetObjectTypesInSystem()
        all_names = shop_api.GetObjectNamesInSystem()

        #Save the objects in the same order every time
        unique_types = list(set(all_types))
        unique_types.sort(reverse=True)

        #Save a list of all 'active' objects with attributes to write
        objects = []
        for obj_type in unique_types:
            
            #Always skip the scenario object if there is only one of them
            if obj_type == "scenario" and all_types.count("scenario") == 1:
                continue
            
            attributes = shop_api.GetObjectTypeAttributeNames(obj_type)
            datatypes = shop_api.GetObjectTypeAttributeDatatypes(obj_type)

            input_attributes = []
            input_datatypes = []
            for attr,dtype in zip(attributes,datatypes):
                
                #Don't include time dependent data if specified
                if static_data_only and (dtype == "txy" or dtype == "xyt"):
                    continue

                #Don't include output attributes
                if shop_api.GetAttributeInfo(obj_type, attr, "isInput") == "False":
                    continue

                #Don't include internal attributes
                if "INTERNAL" in shop_api.GetAttributeInfo(obj_type, attr, "licenseName"):
                    continue

                input_attributes.append(attr)
                input_datatypes.append(dtype)

            obj_names = [name for name,other_type in zip(all_names,all_types) if other_type==obj_type]

            for i,name in enumerate(obj_names):

                active_attributes = []
                active_attribute_names = []
                active_attribute_datatypes = []
                for attr,dtype in zip(input_attributes,input_datatypes):
                    
                    #Skip attributes that are default for the object
                    if shop_api.AttributeIsDefault(obj_type,name,attr):
                        continue             

                    val = get_attribute_value(shop_api,name,obj_type,attr,dtype)
                    
                    #Skip attributes that were actually not active
                    if val is None:
                        continue
                    
                    active_attributes.append(val)
                    active_attribute_names.append(attr)
                    active_attribute_datatypes.append(dtype)

                #Add another active object if there is at least one active input attribute OR the object is an (empty) input object
                if len(active_attributes) > 0 or shop_api.GetObjectInfo(obj_type,"isInput") == "True":
                    obj = {}
                    obj["type"] = obj_type
                    obj["name"] = name

                    if obj_type == "global_settings":
                        obj["code_name"] = "global_settings"
                    else:
                        clean_name = name.lower()
                        #Manually convert nordic characters
                        clean_name = clean_name.replace("æ","ae")
                        clean_name = clean_name.replace("ø","oe")
                        clean_name = clean_name.replace("å","aa")                         

                        #Normalize and convert/ignore other strange characters in the name
                        clean_name = unicodedata.normalize("NFKD", clean_name).encode("ascii", "ignore").decode()

                        #Replace space and remove all special characters that can't be used for variable names in Python
                        clean_name = clean_name.replace(" ","_")
                        illegal_characters = '''~`!@#$%^&*-+={}[]|\/:;"'<>,.?()'''                           
                        clean_name = clean_name.translate({ord(i): None for i in illegal_characters})
                        
                        obj["code_name"] = f"{obj_type}_{clean_name}"

                    obj["attributes"] = active_attributes
                    obj["attribute_names"] = active_attribute_names
                    obj["attribute_datatypes"] = active_attribute_datatypes                     
                    objects.append(obj)
                    
        #Write the active input attributes of each object to the file
        f.write("    #Add all objects and set all attributes\n")
        for obj in objects:
                        
            var_name = obj["code_name"]
            obj_type = obj["type"]
            name = obj["name"]
            
            #Create or retrieve the object depending on if it is an input type or not
            if shop_api.GetObjectInfo(obj_type,"isInput") == "True":
                f.write(f"    {var_name} = shop.model.{obj_type}.add_object('{name}')\n")
            else:
                f.write(f"    {var_name} = shop.model.{obj_type}['{name}']\n")

            #Set all active attributes
            for val,attr,dtype in zip(obj["attributes"],obj["attribute_names"],obj["attribute_datatypes"]):

                if dtype in ["int", "double", "int_array", "double_array"]:
                    f.write(f"    {var_name}.{attr}.set({val})\n")
                elif dtype == "string":
                    f.write(f"    {var_name}.{attr}.set('{val}')\n")
                elif dtype == "string_array":
                    input_list = f"['{val[0]}'"
                    for v in val[1:]:
                        input_list += f", '{v}'"
                    input_list += "]"
                    f.write(f"    {var_name}.{attr}.set({input_list})\n")           
                elif dtype == "sy":
                    f.write(f"    s = {list(val.index)}\n")
                    f.write(f"    y = {list(val.values)}\n")
                    f.write(f"    {var_name}.{attr}.set(pd.Series(y,index=s))\n")                                
                elif dtype == "xy":
                    f.write(f"    x = {list(val.index)}\n")
                    f.write(f"    y = {list(val.values)}\n")
                    f.write(f"    {var_name}.{attr}.set(pd.Series(y,index=x,name={val.name}))\n")    
                elif dtype == "xy_array":
                    f.write("    xy_curves = []\n")
                    for xy in val:
                        f.write(f"    x = {list(xy.index)}\n")
                        f.write(f"    y = {list(xy.values)}\n")
                        f.write(f"    xy_curves.append(pd.Series(y,index=x,name={xy.name}))\n")
                    f.write(f"    {var_name}.{attr}.set(xy_curves)\n") 
                elif dtype == "xyt":
                    f.write("    xyt = []\n")
                    for xy in val:               
                        f.write(f"    x = {list(xy.index)}\n")
                        f.write(f"    y = {list(xy.values)}\n")
                        f.write(f"    xyt.append(pd.Series(y,index=x,name=Timestamp('{str(xy.name)}')))\n")
                    f.write(f"    {var_name}.{attr}.set(xyt)\n")                                                                   
                elif dtype == "txy":
                    val = remove_consecutive_duplicates(val)
                    if len(val.values) > 1:
                        f.write(f"    t = {list(val.index)}\n")
                        f.write(f"    {attr} = {list(val.values)}\n")
                        f.write(f"    {var_name}.{attr}.set(pd.Series({attr},index=t))\n")                  
                    #Use simple syntax if there is only one value in the txy
                    else:
                        f.write(f"    {var_name}.{attr}.set({val.values[0]})\n")                                                                   
            
            f.write("\n")

        #Find and write all connections
        connections = []
        connection_types = ["standard","bypass","spill"]
        
        f.write("\n    #Connect all objects\n")
        for obj in objects:
            
            up_name = obj["code_name"]
            obj_type = obj["type"]
            name = obj["name"]
            
            wrote_connection = False

            for ctype in connection_types:
                
                #Get connected objects for the connection type
                related_indices = shop_api.GetRelations(obj_type, name, f"connection_{ctype}")
            
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
                        if ctype == "standard":
                            f.write(f"    {up_name}.connect_to({down_name})\n")
                        else:
                            f.write(f"    {up_name}.connect_to({down_name},connection_type='{ctype}')\n")
                        wrote_connection = True
            
            #Add a new line when we are done writing connections for an object
            if wrote_connection:
                f.write("\n")

        f.write("    return shop\n\n")

        #Create a function to run all the executed commands in this session
        #There will probably be overlap with the values directly set on the global_settings object, this should not matter
        commands = shop_api.GetExecutedCommands()
        f.write("def run_commands(shop:ShopSession) -> None:\n\n")
        if len(commands) == 0:
            f.write("    #No commands to execute\n")
            f.write("    pass\n")
        else:
            f.write("    #Commands to execute\n")
            for c in commands:
                #Skip reading input commands since the model is already defined
                if "read model" in c or "add model" in c or "read yaml" in c:
                    continue
                f.write(f"    shop.execute_full_command('{c}')\n")

        f.write("\n")
        f.write("shop = get_model()\n")
        f.write("run_commands(shop)\n")