# -*- coding: utf-8 -*-
# Relational
# Copyright (C) 2008  Salvo "LtWorf" Tomaselli
# 
# Relational is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
# author Salvo "LtWorf" Tomaselli <tiposchi@tiscali.it>
try:
    from PyQt4 import QtCore, QtGui
except:
    from PySide import QtCore, QtGui

import compatibility
from relational import maintenance
import platform
import locale

class surveyForm (QtGui.QWidget):
    '''This class is the form used for the survey, needed to intercept the events.
    It also sends the data with http POST to a page hosted on galileo'''
    def setUi(self,ui):
        self.ui=ui
    def setDefaultValues(self):
        '''Sets default values into the form GUI. It has to be
        called after the form has been initialized'''
        
        #Dictionary with country codes
        countries={'BD': 'BANGLADESH', 'BE': 'BELGIUM', 'BF': 'BURKINA FASO', 'BG': 'BULGARIA', 'BA': 'BOSNIA AND HERZEGOVINA', 'BB': 'BARBADOS', 'WF': 'WALLIS AND FUTUNA', 'BL': 'SAINT BARTH\xc3\x89LEMY', 'BM': 'BERMUDA', 'BN': 'BRUNEI DARUSSALAM', 'BO': 'BOLIVIA, PLURINATIONAL STATE OF', 'BH': 'BAHRAIN', 'BI': 'BURUNDI', 'BJ': 'BENIN', 'BT': 'BHUTAN', 'JM': 'JAMAICA', 'BV': 'BOUVET ISLAND', 'BW': 'BOTSWANA', 'WS': 'SAMOA', 'BR': 'BRAZIL', 'BS': 'BAHAMAS', 'JE': 'JERSEY', 'BY': 'BELARUS', 'BZ': 'BELIZE', 'RU': 'RUSSIAN FEDERATION', 'RW': 'RWANDA', 'RS': 'SERBIA', 'TL': 'TIMOR-LESTE', 'RE': 'R\xc3\x89UNION', 'TM': 'TURKMENISTAN', 'TJ': 'TAJIKISTAN', 'RO': 'ROMANIA', 'TK': 'TOKELAU', 'GW': 'GUINEA-BISSAU', 'GU': 'GUAM', 'GT': 'GUATEMALA', 'GS': 'SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS', 'GR': 'GREECE', 'GQ': 'EQUATORIAL GUINEA', 'GP': 'GUADELOUPE', 'JP': 'JAPAN', 'GY': 'GUYANA', 'GG': 'GUERNSEY', 'GF': 'FRENCH GUIANA', 'GE': 'GEORGIA', 'GD': 'GRENADA', 'GB': 'UNITED KINGDOM', 'GA': 'GABON', 'GN': 'GUINEA', 'GM': 'GAMBIA', 'GL': 'GREENLAND', 'GI': 'GIBRALTAR', 'GH': 'GHANA', 'OM': 'OMAN', 'TN': 'TUNISIA', 'JO': 'JORDAN', 'HR': 'CROATIA', 'HT': 'HAITI', 'HU': 'HUNGARY', 'HK': 'HONG KONG', 'HN': 'HONDURAS', 'HM': 'HEARD ISLAND AND MCDONALD ISLANDS', 'VE': 'VENEZUELA, BOLIVARIAN REPUBLIC OF', 'PR': 'PUERTO RICO', 'PS': 'PALESTINIAN TERRITORY, OCCUPIED', 'PW': 'PALAU', 'PT': 'PORTUGAL', 'KN': 'SAINT KITTS AND NEVIS', 'PY': 'PARAGUAY', 'IQ': 'IRAQ', 'PA': 'PANAMA', 'PF': 'FRENCH POLYNESIA', 'PG': 'PAPUA NEW GUINEA', 'PE': 'PERU', 'PK': 'PAKISTAN', 'PH': 'PHILIPPINES', 'PN': 'PITCAIRN', 'PL': 'POLAND', 'PM': 'SAINT PIERRE AND MIQUELON', 'ZM': 'ZAMBIA', 'EH': 'WESTERN SAHARA', 'EE': 'ESTONIA', 'EG': 'EGYPT', 'ZA': 'SOUTH AFRICA', 'EC': 'ECUADOR', 'IT': 'ITALY', 'VN': 'VIET NAM', 'SB': 'SOLOMON ISLANDS', 'ET': 'ETHIOPIA', 'SO': 'SOMALIA', 'ZW': 'ZIMBABWE', 'SA': 'SAUDI ARABIA', 'ES': 'SPAIN', 'ER': 'ERITREA', 'ME': 'MONTENEGRO', 'MD': 'MOLDOVA, REPUBLIC OF', 'MG': 'MADAGASCAR', 'MF': 'SAINT MARTIN', 'MA': 'MOROCCO', 'MC': 'MONACO', 'UZ': 'UZBEKISTAN', 'MM': 'MYANMAR', 'ML': 'MALI', 'MO': 'MACAO', 'MN': 'MONGOLIA', 'MH': 'MARSHALL ISLANDS', 'MK': 'MACEDONIA, THE FORMER YUGOSLAV REPUBLIC OF', 'MU': 'MAURITIUS', 'MT': 'MALTA', 'MW': 'MALAWI', 'MV': 'MALDIVES', 'MQ': 'MARTINIQUE', 'MP': 'NORTHERN MARIANA ISLANDS', 'MS': 'MONTSERRAT', 'MR': 'MAURITANIA', 'IM': 'ISLE OF MAN', 'UG': 'UGANDA', 'TZ': 'TANZANIA, UNITED REPUBLIC OF', 'MY': 'MALAYSIA', 'MX': 'MEXICO', 'IL': 'ISRAEL', 'FR': 'FRANCE', 'AW': 'ARUBA', 'SH': 'SAINT HELENA', 'SJ': 'SVALBARD AND JAN MAYEN', 'FI': 'FINLAND', 'FJ': 'FIJI', 'FK': 'FALKLAND ISLANDS (MALVINAS)', 'FM': 'MICRONESIA, FEDERATED STATES OF', 'FO': 'FAROE ISLANDS', 'NI': 'NICARAGUA', 'NL': 'NETHERLANDS', 'NO': 'NORWAY', 'NA': 'NAMIBIA', 'VU': 'VANUATU', 'NC': 'NEW CALEDONIA', 'NE': 'NIGER', 'NF': 'NORFOLK ISLAND', 'NG': 'NIGERIA', 'NZ': 'NEW ZEALAND', 'NP': 'NEPAL', 'NR': 'NAURU', 'NU': 'NIUE', 'CK': 'COOK ISLANDS', 'CI': "C\xc3\x94TE D'IVOIRE", 'CH': 'SWITZERLAND', 'CO': 'COLOMBIA', 'CN': 'CHINA', 'CM': 'CAMEROON', 'CL': 'CHILE', 'CC': 'COCOS (KEELING) ISLANDS', 'CA': 'CANADA', 'CG': 'CONGO', 'CF': 'CENTRAL AFRICAN REPUBLIC', 'CD': 'CONGO, THE DEMOCRATIC REPUBLIC OF THE', 'CZ': 'CZECH REPUBLIC', 'CY': 'CYPRUS', 'CX': 'CHRISTMAS ISLAND', 'CR': 'COSTA RICA', 'CV': 'CAPE VERDE', 'CU': 'CUBA', 'SZ': 'SWAZILAND', 'SY': 'SYRIAN ARAB REPUBLIC', 'KG': 'KYRGYZSTAN', 'KE': 'KENYA', 'SR': 'SURINAME', 'KI': 'KIRIBATI', 'KH': 'CAMBODIA', 'SV': 'EL SALVADOR', 'KM': 'COMOROS', 'ST': 'SAO TOME AND PRINCIPE', 'SK': 'SLOVAKIA', 'KR': 'KOREA, REPUBLIC OF', 'SI': 'SLOVENIA', 'KP': "KOREA, DEMOCRATIC PEOPLE'S REPUBLIC OF", 'KW': 'KUWAIT', 'SN': 'SENEGAL', 'SM': 'SAN MARINO', 'SL': 'SIERRA LEONE', 'SC': 'SEYCHELLES', 'KZ': 'KAZAKHSTAN', 'KY': 'CAYMAN ISLANDS', 'SG': 'SINGAPORE', 'SE': 'SWEDEN', 'SD': 'SUDAN', 'DO': 'DOMINICAN REPUBLIC', 'DM': 'DOMINICA', 'DJ': 'DJIBOUTI', 'DK': 'DENMARK', 'VG': 'VIRGIN ISLANDS, BRITISH', 'DE': 'GERMANY', 'YE': 'YEMEN', 'DZ': 'ALGERIA', 'US': 'UNITED STATES', 'UY': 'URUGUAY', 'YT': 'MAYOTTE', 'UM': 'UNITED STATES MINOR OUTLYING ISLANDS', 'LB': 'LEBANON', 'LC': 'SAINT LUCIA', 'LA': "LAO PEOPLE'S DEMOCRATIC REPUBLIC", 'TV': 'TUVALU', 'TW': 'TAIWAN, PROVINCE OF CHINA', 'TT': 'TRINIDAD AND TOBAGO', 'TR': 'TURKEY', 'LK': 'SRI LANKA', 'LI': 'LIECHTENSTEIN', 'LV': 'LATVIA', 'TO': 'TONGA', 'LT': 'LITHUANIA', 'LU': 'LUXEMBOURG', 'LR': 'LIBERIA', 'LS': 'LESOTHO', 'TH': 'THAILAND', 'TF': 'FRENCH SOUTHERN TERRITORIES', 'TG': 'TOGO', 'TD': 'CHAD', 'TC': 'TURKS AND CAICOS ISLANDS', 'LY': 'LIBYAN ARAB JAMAHIRIYA', 'VA': 'HOLY SEE (VATICAN CITY STATE)', 'VC': 'SAINT VINCENT AND THE GRENADINES', 'AE': 'UNITED ARAB EMIRATES', 'AD': 'ANDORRA', 'AG': 'ANTIGUA AND BARBUDA', 'AF': 'AFGHANISTAN', 'AI': 'ANGUILLA', 'VI': 'VIRGIN ISLANDS, U.S.', 'IS': 'ICELAND', 'IR': 'IRAN, ISLAMIC REPUBLIC OF', 'AM': 'ARMENIA', 'AL': 'ALBANIA', 'AO': 'ANGOLA', 'AN': 'NETHERLANDS ANTILLES', 'AQ': 'ANTARCTICA', 'AS': 'AMERICAN SAMOA', 'AR': 'ARGENTINA', 'AU': 'AUSTRALIA', 'AT': 'AUSTRIA', 'IO': 'BRITISH INDIAN OCEAN TERRITORY', 'IN': 'INDIA', 'AX': '\xc3\x85LAND ISLANDS', 'AZ': 'AZERBAIJAN', 'IE': 'IRELAND', 'ID': 'INDONESIA', 'UA': 'UKRAINE', 'QA': 'QATAR', 'MZ': 'MOZAMBIQUE'}
        
        #Setting system string
        try:
            self.ui.txtSystem.setText(platform.platform())
            self.ui.txtSystem.setCursorPosition(0)
        except:
            pass
        
        #Getting country from locale code
        try:
            locale.setlocale(locale.LC_ALL,'')
            country_code=locale.getlocale()[0].split('_')[1]
        
            self.ui.txtCountry.setText(countries[country_code])
            self.ui.txtCountry.setCursorPosition(0)
        except:
            pass
    def send(self):
        '''Sends the data inserted in the form'''
        
        post={}
        post['software']="Relational algebra"
        post["version"]= version
        post["system"]= compatibility.get_py_str(self.ui.txtSystem.text())
        post["country"]= compatibility.get_py_str(self.ui.txtCountry.text())
        post["school"]= compatibility.get_py_str(self.ui.txtSchool.text())
        post["age"] = compatibility.get_py_str(self.ui.txtAge.text())
        post["find"] = compatibility.get_py_str(self.ui.txtFind.text())
        post["email"] = compatibility.get_py_str(self.ui.txtEmail.text())
        post["comments"] = compatibility.get_py_str(self.ui.txtComments.toPlainText())
    
        #Clears the form
        self.ui.txtSystem.clear()
        self.ui.txtCountry.clear()
        self.ui.txtSchool.clear()
        self.ui.txtAge.clear()
        self.ui.txtFind.clear()
        self.ui.txtEmail.clear()
        self.ui.txtComments.clear()
        
        response=maintenance.send_survey(post)
    
        if response.status!=200:
            QtGui.QMessageBox.information(None,QtGui.QApplication.translate("Form", "Error"),QtGui.QApplication.translate("Form", "Unable to send the data!")  )
        else:
            QtGui.QMessageBox.information(None,QtGui.QApplication.translate("Form", "Thanks"),QtGui.QApplication.translate("Form", "Thanks for sending!")  )
      
        self.hide()
