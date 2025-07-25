# -*- coding: utf-8 -*-

'''
/***************************************************************************
 DrainageBasinGeomorphology
                                 A QGIS plugin
 This plugin provides tools for geomorphological analysis in drainage basins.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2025-03-22
        copyright            : (C) 2025 by João Vitor Pimenta
        email                : jvpjoaopimenta@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
'''

__author__ = 'João Vitor Pimenta'
__date__ = '2025-03-22'
__copyright__ = '(C) 2025 by João Vitor Pimenta'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean)
from .algorithms.EAVAboveBelowProcessing import runEAVAboveBelow, verifyLibs

class EAVAboveBelowCalc(QgsProcessingAlgorithm):
    '''
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    '''

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    ELEVATION_AREA_VOLUME_DATA = 'ELEVATION_AREA_VOLUME_DATA'
    DRAINAGE_BASINS = 'DRAINAGE_BASINS'
    DEM = 'DEM'
    DISTANCE_BETWEEN_CONTOUR_LINES = 'DISTANCE_BETWEEN_CONTOUR_LINES'
    USE_ONLY_DEM_VALUES = 'USE_ONLY_DEM_VALUES'
    BASE_LEVEL_MINIMUM = 'BASE_LEVEL_MINIMUM'
    USE_MIN_VALUE_DEM = 'USE_MIN_VALUE_DEM'
    BASE_LEVEL_MAXIMUM = 'BASE_LEVEL_MAXIMUM'
    USE_MAX_VALUE_DEM = 'USE_MAX_VALUE_DEM'
    SUBTRACTS_VOLUME_BELOW = 'SUBTRACTS_VOLUME_BELOW'
    GRAPH = 'GRAPH'


    def initAlgorithm(self, config):
        '''
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        '''

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.DRAINAGE_BASINS,
                self.tr('Drainage basins'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.DEM,
                self.tr('DEM'),
                [QgsProcessing.TypeRaster]
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.DISTANCE_BETWEEN_CONTOUR_LINES,
                self.tr('Distance between contour lines'),
                type=QgsProcessingParameterNumber.Double,
                minValue=0,
                defaultValue=10
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.USE_ONLY_DEM_VALUES,
                self.tr('Use only the elevation values ​​from the DEM'),
                defaultValue=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.BASE_LEVEL_MINIMUM,
                self.tr('Minimum level'),
                type=QgsProcessingParameterNumber.Double,
                minValue=0,
                defaultValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.USE_MIN_VALUE_DEM,
                self.tr('Use the minimum elevation value of the DEM as minimum level'),
                defaultValue=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.BASE_LEVEL_MAXIMUM,
                self.tr('Maximum level'),
                type=QgsProcessingParameterNumber.Double,
                minValue=0,
                defaultValue=1000
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.USE_MAX_VALUE_DEM,
                self.tr('Use the maximum elevation value of the DEM as maximum level'),
                defaultValue=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SUBTRACTS_VOLUME_BELOW,
                self.tr('Subtracts values below from values above, instead of subtracting values above from values below'),
                defaultValue=False,
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.ELEVATION_AREA_VOLUME_DATA,
                self.tr('Elevation area volume data'),
                fileFilter=('CSV files (*.csv)')
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.GRAPH,
                self.tr('Graph'),
                fileFilter=('HTML files (*.html)')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        '''
        Here is where the processing itself takes place.
        '''

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        basinSource = self.parameterAsSource(parameters, self.DRAINAGE_BASINS, context)

        demLayer = self.parameterAsRasterLayer(parameters, self.DEM, context)

        distanceCurves = self.parameterAsInt(parameters, self.DISTANCE_BETWEEN_CONTOUR_LINES, context)

        useOnlyRasterElev = self.parameterAsBoolean(parameters, self.USE_ONLY_DEM_VALUES, context)

        minLevel = self.parameterAsDouble(parameters, self.BASE_LEVEL_MINIMUM, context)

        useMinRasterElev = self.parameterAsBoolean(parameters, self.USE_MIN_VALUE_DEM, context)

        maxLevel = self.parameterAsDouble(parameters, self.BASE_LEVEL_MAXIMUM, context)

        useMaxRasterElev = self.parameterAsBoolean(parameters, self.USE_MAX_VALUE_DEM, context)

        subtractsBelow = self.parameterAsBoolean(parameters, self.SUBTRACTS_VOLUME_BELOW, context)

        pathData = self.parameterAsFileOutput(parameters, self.ELEVATION_AREA_VOLUME_DATA, context)

        pathGraph = self.parameterAsString(parameters, self.GRAPH, context)

        verifyLibs()
        runEAVAboveBelow(basinSource,demLayer,pathData,pathGraph,distanceCurves,minLevel,maxLevel,subtractsBelow,useOnlyRasterElev,useMinRasterElev,useMaxRasterElev,feedback)

        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {self.ELEVATION_AREA_VOLUME_DATA: pathData,
                self.GRAPH: pathGraph}

    def name(self):
        '''
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        '''
        return 'Calculate elevation-area-volume above and below'

    def displayName(self):
        '''
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        '''
        return self.tr(self.name())

    def group(self):
        '''
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        '''
        return self.tr(self.groupId())

    def icon(self):
        """
        Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        return QIcon(os.path.join(os.path.dirname(__file__), "icon.png"))

    def shortHelpString(self):
        """
        Returns a localised short help string for the algorithm.
        """
        return self.tr("""
        <html>
            <body>
                <p>       
        This tool calculates elevation - area - volume (above/below) for each basin feature individually.               
                </p>
                <p>
        <strong>Drainage basins: </strong>Layer containing drainage basins as features.
        <strong>DEM: </strong>Raster containing the band with the altimetry of the drainage basins. 
        <strong>Distance between contour lines: </strong>It is the distance between the contour lines within the basin boundary.
        <strong>Elevation area volume data: </strong>File with elevation - area - volume (above/below) data calculated individually for each basin.
        <strong>Graphs: </strong>Folder containing the elevation-area-volume (above/below) graph for each basin individually.        

        The use of a projected CRS is recommended (the plugin calculation assumes that all input layers are in projected coordinate reference systems).

        If you need more information about how the plugin works, such as the calculations it performs, among other things, access: https://github.com/JoaoVitorPimenta/qgis-plugin-Drainage-Basin-Geomorphology
        If you have found any bugs, errors or have any requests to make, among other things, please acess: https://github.com/JoaoVitorPimenta/qgis-plugin-Drainage-Basin-Geomorphology/issues
        If you need training for the plugin, or want to contact the plugin author for any reason, send an email to: jvpjoaopimentadev@gmail.com                </p>
            </body>
        </html>
                    """)

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return EAVAboveBelowCalc()
