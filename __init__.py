# -*- coding: utf-8 -*-
"""
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
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'João Vitor Pimenta'
__date__ = '2025-03-22'
__copyright__ = '(C) 2025 by João Vitor Pimenta'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load DrainageBasinGeomorphology class from file DrainageBasinGeomorphology.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Drainage_Basin_Morphology import DrainageBasinGeomorphologyPlugin
    return DrainageBasinGeomorphologyPlugin()
