import arcpy, sys, os
arcpy.env.overwriteOutput = True

cityMains = arcpy.GetParameterAsText(0) #the city's gravity mains GIS data
surveyedMains = arcpy.GetParameterAsText(1) #surveyed gravity mains GIS data
manholesIntegrated = arcpy.GetParameterAsText(2) #manholes that have information already integrated

workspace = os.path.dirname(os.path.dirname(cityMains)) # must set a workspace for the edit session - use the location of the Checkout database

edit = arcpy.da.Editor(workspace) #set workspace to have an edit session
edit.startEditing(False,True) #start without a redo/undo stack for versioned data, more efficient
edit.startOperation() #start editting

containsZ1MHA = arcpy.GetParameter(3) #boolean value for updating newly found assets
materialBoolean = arcpy.GetParameter(4) #boolean value for customized fields
diameterBoolean = arcpy.GetParameter(5) #boolean value for customized fields
upstreamDownstreamBoolean = arcpy.GetParameter(6) #boolean value for customized fields
lifecycleBoolean = arcpy.GetParameter(7) #boolean value for customized fields
dataSourceBoolean = arcpy.GetParameter(8) #boolean value for customized fields


fieldsMains = ['FACILITYID', 'MATERIAL', 'DIAMETER', 'FROMMH', 'TOMH', 'DSDEPTHFROMRIM', 'DOWNELEV', 'USDEPTHFROMRIM', 'UPELEV', 'SLOPE', 'LIFECYCLESTATUS', 'DATASOURCE', 'LEGACYPIPEASSETID']
fieldsManholes = ['FACILITYID', 'INVERT', 'INVERTELEV', 'RIMELEV', 'RIMTOGRADE', 'LIFECYCLESTATUS', 'GPSDATE', 'DATASOURCE']

if (materialBoolean or diameterBoolean or upstreamDownstreamBoolean or lifecycleBoolean or dataSourceBoolean) and not containsZ1MHA: # update attributes that are customized
    arcpy.AddMessage('Updating personalized attributes.')

    with arcpy.da.SearchCursor(surveyedMains, fieldsMains) as cursor:
        for surveyRow in cursor:

            surveyedGravityMainID = str(surveyRow[0]) # grab the current surveyed main FacilityID and search for it in the City's database

            with arcpy.da.UpdateCursor(cityMains, fieldsMains, where_clause = "\"FACILITYID\" = " + "'" + surveyedGravityMainID + "'") as cursor2:
                for cityRow in cursor2:

                    if cityRow[0] == surveyRow[0] and cityRow[2] < 15: # see if the facility IDs match from the survey and city. DON'T TOUCH MAJOR MAINS!!!! Update attribute field values only if the survey data are not null or unknown!!!

                        if surveyRow[1] != "None" and surveyRow[1] != 'XXX' and materialBoolean: # Material

                            cityRow[1] = surveyRow[1]
                            cursor2.updateRow(cityRow)

                        if surveyRow[2] != "None" and surveyRow[1] != 0 and diameterBoolean: # Diameter

                            cityRow[2] = surveyRow[2]
                            cursor2.updateRow(cityRow)

                        if surveyRow[10] != "None" and lifecycleBoolean:  #Lifecycle status

                            cityRow[10] = surveyRow[10]
                            cursor2.updateRow(cityRow)

                        if surveyRow[11] != "None" and dataSourceBoolean: #Datasource

                            cityRow[11] = surveyRow[11]
                            cursor2.updateRow(cityRow)
            del cursor2
    del cursor

    arcpy.AddMessage('Surveyed main attributes have been updated. Working on transfering upstream and downstream attributes, if so desired.')

    if upstreamDownstreamBoolean: #update customized field if wanted

            with arcpy.da.SearchCursor(manholesIntegrated, fieldsManholes) as cursor: #Updating upstream attributes
                for surveyRow in cursor:

                    surveyedManholeID = str(surveyRow[0]) # grab the integrated manhole ID

                    with arcpy.da.UpdateCursor(cityMains, fieldsMains, where_clause = "\"FROMMH\" = " + "'" + surveyedManholeID + "'") as cursor2: # use a query to select all the FROMMH rows from the mains
                        for cityRow in cursor2:

                            if cityRow[3] == surveyRow[0] and cityRow[2] < 15: # DON'T TOUCH MAJORS!!!! If the from manhole matches the manhole facilityID, update it if it isn't null.

                                if surveyRow[1] != "None" and surveyRow[1] != 0 : # US depth from rim

                                    cityRow[7] = surveyRow[1]
                                    cursor2.updateRow(cityRow)

                                if surveyRow[2] != "None" and surveyRow[2] != 0:  #US elevation

                                    cityRow[8] = surveyRow[2]
                                    cursor2.updateRow(cityRow)

                    del cursor2
            del cursor

            with arcpy.da.SearchCursor(manholesIntegrated, fieldsManholes) as cursor: #Updating downstream attributes
                for surveyRow in cursor:

                    surveyedManholeID = str(surveyRow[0]) # grab the integrated manhole ID

                    with arcpy.da.UpdateCursor(cityMains, fieldsMains, where_clause = "\"TOMH\" = " + "'" + surveyedManholeID + "'") as cursor2: # use a query to select all the TOMH rows from the mains
                        for cityRow in cursor2:

                            if cityRow[4] == surveyRow[0] and cityRow[2] < 15: # DON'T TOUCH MAJORS!!!! If the to manhole matches the manhole facilityID, update it if it isn't null.

                                if surveyRow[1] != "None" and surveyRow[1] != 0: # DS depth from rim

                                    cityRow[5] = surveyRow[1]
                                    cursor2.updateRow(cityRow)

                                if surveyRow[2] != "None" and surveyRow[1] != 0:  #DS elevation

                                    cityRow[6] = surveyRow[2]
                                    cursor2.updateRow(cityRow)
                    del cursor2
            del cursor

    arcpy.AddMessage("Script finished.")
    edit.stopOperation()
    edit.stopEditing(True) #stop the edit session and save edits
    sys.exit()








if (materialBoolean or diameterBoolean or upstreamDownstreamBoolean or lifecycleBoolean or dataSourceBoolean) and containsZ1MHA: # update attributes that are customized and are newly discovered
    arcpy.AddMessage('Updating personalized attributes for newly found assets.')

    with arcpy.da.SearchCursor(surveyedMains, fieldsMains) as cursor:
        for surveyRow in cursor:

            surveyedGravityMainID = str(surveyRow[0]) # grab the current surveyed main FacilityID and search for it in the City's database

            with arcpy.da.UpdateCursor(cityMains, fieldsMains, where_clause = "\"LEGACYPIPEASSETID\" = " + "'" + surveyedGravityMainID + "'") as cursor2:
                for cityRow in cursor2:

                    if cityRow[0] == surveyRow[0] and cityRow[2] < 15: # see if the facility IDs match from the survey and city. DON'T TOUCH MAJOR MAINS!!!! Update attribute field values only if the survey data are not null or unknown!!!

                        if surveyRow[1] != "None" and surveyRow[1] != 'XXX' and materialBoolean: # Material

                            cityRow[1] = surveyRow[1]
                            cursor2.updateRow(cityRow)

                        if surveyRow[2] != "None" and surveyRow[1] != 0 and diameterBoolean: # Diameter

                            cityRow[2] = surveyRow[2]
                            cursor2.updateRow(cityRow)

                        if surveyRow[10] != "None" and lifecycleBoolean:  #Lifecycle status

                            cityRow[10] = surveyRow[10]
                            cursor2.updateRow(cityRow)

                        if surveyRow[11] != "None" and dataSourceBoolean: #Datasource

                            cityRow[11] = surveyRow[11]
                            cursor2.updateRow(cityRow)
            del cursor2
    del cursor

    arcpy.AddMessage('Surveyed main attributes have been updated. Working on transfering upstream and downstream attributes, if so desired for the newly found assets.')

    if upstreamDownstreamBoolean: #update customized field if wanted

            with arcpy.da.SearchCursor(manholesIntegrated, fieldsManholes) as cursor: #Updating upstream attributes
                for surveyRow in cursor:

                    surveyedManholeID = str(surveyRow[0]) # grab the integrated manhole ID

                    with arcpy.da.UpdateCursor(cityMains, fieldsMains, where_clause = "\"FROMMH\" = " + "'" + surveyedManholeID + "'") as cursor2: # use a query to select all the FROMMH rows from the mains
                        for cityRow in cursor2:

                            if cityRow[3] == surveyRow[0] and cityRow[2] < 15: # DON'T TOUCH MAJORS!!!! If the from manhole matches the manhole facilityID, update it if it isn't null.

                                if surveyRow[1] != "None" and surveyRow[1] != 0 : # US depth from rim

                                    cityRow[7] = surveyRow[1]
                                    cursor2.updateRow(cityRow)

                                if surveyRow[2] != "None" and surveyRow[2] != 0:  #US elevation

                                    cityRow[8] = surveyRow[2]
                                    cursor2.updateRow(cityRow)
                    del cursor2
            del cursor

            with arcpy.da.SearchCursor(manholesIntegrated, fieldsManholes) as cursor: #Updating downstream attributes
                for surveyRow in cursor:

                    surveyedManholeID = str(surveyRow[0]) # grab the integrated manhole ID

                    with arcpy.da.UpdateCursor(cityMains, fieldsMains, where_clause = "\"TOMH\" = " + "'" + surveyedManholeID + "'") as cursor2: # use a query to select all the TOMH rows from the mains
                        for cityRow in cursor2:

                            if cityRow[4] == surveyRow[0] and cityRow[2] < 15: # DON'T TOUCH MAJORS!!!! If the to manhole matches the manhole facilityID, update it if it isn't null.

                                if surveyRow[1] != "None" and surveyRow[1] != 0: # DS depth from rim

                                    cityRow[5] = surveyRow[1]
                                    cursor2.updateRow(cityRow)

                                if surveyRow[2] != "None" and surveyRow[1] != 0:  #DS elevation

                                    cityRow[6] = surveyRow[2]
                                    cursor2.updateRow(cityRow)
                    del cursor2
            del cursor

    arcpy.AddMessage("Script finished.")
    edit.stopOperation()
    edit.stopEditing(True) #stop the edit session and save edits
    sys.exit()