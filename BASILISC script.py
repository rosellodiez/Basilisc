#Script to define threshold on DICOM images of uCT scans, segment individual bones to be analyzed, and create + export 3D models of the desired elements

#Created by: Santiago 
#Date created: 28/04/2019
import os
import subprocess

#Creating mask for bones
mask_all = mimics.segment.create_mask()
mask_all.name = "ALL"

#setting threshold based on developmental stage
mask_all = mimics.data.masks[0]
threshold = mimics.dialogs.question_box(message = "Select developmental stage of sample", title = "Threshold", buttons = "E17.5;P7")
if threshold == "E17.5":
    low_hu = 195
    high_hu = 2000
    l_t = mimics.segment.HU2GV(low_hu)
    h_t = mimics.segment.HU2GV(high_hu)
    mimics.segment.threshold(mask=mask_all,threshold_min=l_t,threshold_max=h_t)
elif threshold == "P7":
    low_hu = 398
    high_hu = 5000
    l_t = mimics.segment.HU2GV(low_hu)
    h_t = mimics.segment.HU2GV(high_hu)
    mimics.segment.threshold(mask=mask_all,threshold_min=l_t,threshold_max=h_t)

#defining landmarks
mask = "Threshold"
landmark = ("RIGHT HUMERUS", "LEFT HUMERUS", "RIGHT RADIUS", "LEFT RADIUS", "RIGHT FEMUR", "LEFT FEMUR", "RIGHT TIBIA", "LEFT TIBIA")

#Function to ask user to select given landmark/element
def indicate_landmark (pid):
    element = landmark[pid]
    name = element
            
    try:
        #skip through element if not present
        sel = mimics.dialogs.question_box(message="Select if {} is present, or skip if this element is not present".format(element), title="Region Selection", buttons= 'Select;Skip')
        if sel == "Skip":
            skip = True
        
        elif sel == "Select":        
            coordinate = mimics.analyze.indicate_point(message='Select point on {}'.format(element), confirm=False, show_message_box=True)
            element_point = coordinate.coordinates
            element_point = tuple (element_point)
            #build the mask
            mask = mimics.segment.region_grow(point= element_point, input_mask= mask_all, target_mask=None, slice_type= "Axial",keep_original_mask=True)
            mask.name = '{}'.format(element)
                                    
    except InterruptedError:
        return False
    
#Function to create 3D parts
def create_3D():
    #if text file has already been created, delete contents
    open("{} measurements.txt".format(threshold),"w").close()     
    for p in mimics.data.masks:
        if p.name in landmark:
            par = mimics.segment.calculate_part(p,"High")
            par.name = p.name   
            #creating fitted lines to part
            line = mimics.analyze.create_line_fit_to_surface(part=par,name="{} fitted line".format(par.name))
            measurement = str(line.length)
            with open(os.path.join(os.path.split(__file__)[0],"{} measurements.txt".format(threshold)),"a+") as f:
                f.write("{},{}".format(par.name,measurement) + "\n")
                f.close()
            #export STL
            root_path = os.path.split(os.path.abspath(__file__))[0]
            path_stl = os.path.join(root_path,par.name + ".stl")
            mimics.file.export_part(par,path_stl)
            #write stl directory into text file
            with open(os.path.join(os.path.split(__file__)[0],"{} Stls.txt".format(threshold)),"a+") as f:
                f.write(path_stl + "\n")
                f.close()                                        
    return
    
#EXECUTE FUNCTIONS CREATED
#go through all given landmarks
for l in landmark:
    indicate_landmark(landmark.index(l)) 
#create 3D parts
create_3D()


#change directory to folder where script is stored
os.chdir("C:\\users\\bsantiag\\Documents\\BASILISC Scripts")            
#save file
mimics.file.save_project(filename= "{} Automated Segmentation".format(threshold))