import arcpy, sys, os
arcpy.env.overwriteOutput = True

cityMains = arcpy.GetParameterAsText(0) # the city's gravity main feature class
surveyedMains = arcpy.GetParameterAsText(1) # the surveyed gravity mains feature class

workspace = os.path.dirname(os.path.dirname(cityMains)) # must set a workspace for the edit session - use the location of the Checkout database
arcpy.AddMessage('Editting database location ' + workspace)

edit = arcpy.da.Editor(workspace) #set workspace to have an edit session
edit.startEditing(False,True) #start without a redo/undo stack for versioned data, more efficient
edit.startOperation() #start editting

containsZ1MHA = arcpy.GetParameter(2) #boolean value for updating newly found assets
materialBoolean = arcpy.GetParameter(3) #boolean value for customized fields
diameterBoolean = arcpy.GetParameter(4) #boolean value for customized fields
upstreamDownstreamBoolean = arcpy.GetParameter(5) #boolean value for customized fields
lifecycleBoolean = arcpy.GetParameter(6) #boolean value for customized fields
dataSourceBoolean = arcpy.GetParameter(7) #boolean value for customized fields

fieldsMains = ['FACILITYID', 'MATERIAL', 'DIAMETER', 'FROMMH', 'TOMH', 'DSDEPTHFROMRIM', 'DOWNELEV', 'USDEPTHFROMRIM', 'UPELEV', 'SLOPE', 'LIFECYCLESTATUS', 'DATASOURCE', 'LEGACYPIPEASSETID'] # field names to be used for the cursors

if not materialBoolean and not diameterBoolean and not upstreamDownstreamBoolean and not lifecycleBoolean and not dataSourceBoolean: # none of the fields were specified to be updated
    arcpy.AddMessage('Must specify fields to update!')
    sys.exit()

surveyedMainsTuple = arcpy.da.SearchCursor(surveyedMains, fieldsMains) # save the search cursor of the surveyed mains to a tuple

if (materialBoolean or diameterBoolean or upstreamDownstreamBoolean or lifecycleBoolean or dataSourceBoolean) and not containsZ1MHA: # update attributes that are customized
    arcpy.AddMessage('Updating personalized attributes.')

    with arcpy.da.UpdateCursor(cityMains, fieldsMains) as cursor: # create an update cursor to update the city's gravity main feature class

        for cityRow in cursor:

            for surveyedMainRow in surveyedMainsTuple: # use a for loop to loop through each surveyed main to find a match to the current row in the city's gravity main feature class

                surveyedMainRowFacilityID = surveyedMainRow[0] # FacilityID of the surveyed main
                surveyedMainRowMaterial = surveyedMainRow[1] # material of the surveyed main
                surveyedMainRowDiameter = surveyedMainRow[2] # diameter of the surveyed main
                surveyedMainRowDSDepth = surveyedMainRow[5] # DS Depth of the surveyed main
                surveyedMainRowDSElev = surveyedMainRow[6] # DS elevation of the surveyed main
                surveyedMainRowUSDepth = surveyedMainRow[7] # US elevation of the surveyed main
                surveyedMainRowUSElev = surveyedMainRow[8] # US Depth of the surveyed main
                surveyedMainRowSlope = surveyedMainRow[9] # Slope of the surveyed main
                surveyedMainRowLifecycle = surveyedMainRow[10] # lifecycle status of the surveyed main
                surveyedMainRowDataSource = surveyedMainRow[11] # data source of the surveyed main

                if str(cityRow[0]) == surveyedMainRowFacilityID and cityRow[2] < 15: # see if the facility IDs match from the survey and city. DON'T TOUCH MAJOR MAINS!!!! Update attribute field values only if the survey data are not null or unknown!!!

                    if surveyedMainRowMaterial != None and surveyedMainRowMaterial != 'XXX' and surveyedMainRowMaterial != 'CIPP' and materialBoolean: # Material is not null or material is not Cured in Place Pipe and material box is checked

                        cityRow[1] = surveyedMainRowMaterial
                        cursor.updateRow(cityRow)

                    if surveyedMainRowDiameter != None and surveyedMainRowDiameter != 0 and diameterBoolean: # Diameter

                        cityRow[2] = surveyedMainRowDiameter
                        cursor.updateRow(cityRow)

                    if surveyedMainRowDSDepth != None and surveyedMainRowDSDepth != 0 and upstreamDownstreamBoolean: # DS Depth

                        cityRow[5] = surveyedMainRowDSDepth;
                        cursor.updateRow(cityRow)

                    if surveyedMainRowDSElev != None and surveyedMainRowDSElev != 0 and upstreamDownstreamBoolean: # DS Elevation

                        cityRow[6] = surveyedMainRowDSElev;
                        cursor.updateRow(cityRow)

                    if surveyedMainRowUSDepth != None and surveyedMainRowUSDepth != 0 and upstreamDownstreamBoolean: # US Depth

                        cityRow[7] = surveyedMainRowUSDepth;
                        cursor.updateRow(cityRow)

                    if surveyedMainRowUSElev != None and surveyedMainRowUSElev != 0 and upstreamDownstreamBoolean: # US Elevation

                        cityRow[8] = surveyedMainRowUSElev;
                        cursor.updateRow(cityRow)

                    if surveyedMainRowSlope != None and upstreamDownstreamBoolean: # Slope

                        cityRow[9] = surveyedMainRowSlope;
                        cursor.updateRow(cityRow)

                    if surveyedMainRowLifecycle != None and lifecycleBoolean:  # Lifecycle status

                        cityRow[10] = surveyedMainRowLifecycle
                        cursor.updateRow(cityRow)

                    if surveyedMainRowDataSource != None and dataSourceBoolean: # Datasource

                        cityRow[11] = surveyedMainRowDataSource
                        cursor.updateRow(cityRow)

            surveyedMainsTuple.reset() # reset the cursor if it didn't find a match so the search can continue on the next City Row

    del cursor

    arcpy.AddMessage('Surveyed main attributes have been updated.')
    edit.stopOperation()
    edit.stopEditing(True) #stop the edit session and save edits
    sys.exit()


if (materialBoolean or diameterBoolean or upstreamDownstreamBoolean or lifecycleBoolean or dataSourceBoolean) and containsZ1MHA: # update attributes that are customized and are newly discovered
    arcpy.AddMessage('Updating personalized attributes for newly found assets.')

    with arcpy.da.UpdateCursor(cityMains, fieldsMains) as cursor2:
        for cityRow in cursor2:

            for surveyedMainRow in surveyedMainsTuple:

                surveyedMainRowFacilityID = surveyedMainRow[0] # FacilityID of the surveyed main
                surveyedMainRowMaterial = surveyedMainRow[1] # material of the surveyed main
                surveyedMainRowDiameter = surveyedMainRow[2] # diameter of the surveyed main
                surveyedMainRowDSDepth = surveyedMainRow[5] # DS Depth of the surveyed main
                surveyedMainRowDSElev = surveyedMainRow[6] # DS elevation of the surveyed main
                surveyedMainRowUSDepth = surveyedMainRow[7] # US elevation of the surveyed main
                surveyedMainRowUSElev = surveyedMainRow[8] # US Depth of the surveyed main
                surveyedMainRowSlope = surveyedMainRow[9] # Slope of the surveyed main
                surveyedMainRowLifecycle = surveyedMainRow[10] # lifecycle status of the surveyed main
                surveyedMainRowDataSource = surveyedMainRow[11] # data source of the surveyed main

                if cityRow[12] == surveyedMainRowFacilityID and cityRow[2] < 15: # see if the facility IDs match from the survey and city. DON'T TOUCH MAJOR MAINS!!!! Update attribute field values only if the survey data are not null or unknown!!!

                    if surveyedMainRowMaterial != None and surveyedMainRowMaterial != 'XXX' and surveyedMainRowMaterial != 'CIPP' and materialBoolean: # Material

                        cityRow[1] = surveyedMainRowMaterial
                        cursor2.updateRow(cityRow)

                    if surveyedMainRowDiameter != None and surveyedMainRowDiameter != 0 and diameterBoolean: # Diameter

                        cityRow[2] = surveyedMainRowDiameter
                        cursor2.updateRow(cityRow)

                    if surveyedMainRowDSDepth != None and surveyedMainRowDSDepth != 0 and upstreamDownstreamBoolean: # DS Depth

                        cityRow[5] = surveyedMainRowDSDepth;
                        cursor2.updateRow(cityRow)

                    if surveyedMainRowDSElev != None and surveyedMainRowDSElev != 0 and upstreamDownstreamBoolean: # DS Elevation

                        cityRow[6] = surveyedMainRowDSElev;
                        cursor2.updateRow(cityRow)

                    if surveyedMainRowUSDepth != None and surveyedMainRowUSDepth != 0 and upstreamDownstreamBoolean: # US Depth

                        cityRow[7] = surveyedMainRowUSDepth;
                        cursor2.updateRow(cityRow)

                    if surveyedMainRowUSElev != None and surveyedMainRowUSElev != 0 and upstreamDownstreamBoolean: # US Elevation

                        cityRow[8] = surveyedMainRowUSElev;
                        cursor2.updateRow(cityRow)

                    if surveyedMainRowSlope != None and upstreamDownstreamBoolean: # Slope

                        cityRow[9] = surveyedMainRowSlope;
                        cursor2.updateRow(cityRow)

                    if surveyedMainRowLifecycle != None and lifecycleBoolean:  # Lifecycle status

                        cityRow[10] = surveyedMainRowLifecycle
                        cursor2.updateRow(cityRow)

                    if surveyedMainRowDataSource != None and dataSourceBoolean: # Datasource

                        cityRow[11] = surveyedMainRowDataSource
                        cursor2.updateRow(cityRow)

            surveyedMainsTuple.reset() # reset the cursor so the search can continue on the next City Row

    del cursor2

    arcpy.AddMessage('Surveyed main attributes have been updated. Working on transfering upstream and downstream attributes, if so desired for the newly found assets.')

arcpy.AddMessage("Script finished.")
edit.stopOperation()
edit.stopEditing(True) #stop the edit session and save edits
sys.exit()