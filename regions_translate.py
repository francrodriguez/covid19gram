#!/bin/env python
# -*- coding: utf-8 -*-

from gettext import gettext as _

REGIONS = {
    'Andalucía': _('Andalucía'),
    'Aragón': _('Aragón'),
    'Asturias': _('Asturias'),
    'Baleares': _('Baleares'),
    'Canarias': _('Canarias'),
    'Cantabria': _('Cantabria'),
    'Castilla-La Mancha': _('Castilla-La Mancha'),
    'Castilla y León': _('Castilla y León'),
    'Cataluña': _('Cataluña'),
    'Ceuta': _('Ceuta'),
    'C. Valenciana': _('C. Valenciana'),
    'Extremadura': _('Extremadura'),
    'Galicia': _('Galicia'),
    'Madrid': _('Madrid'),
    'Melilla': _('Melilla'),
    'Murcia': _('Murcia'),
    'Navarra': _('Navarra'),
    'País Vasco': _('País Vasco'),
    'La Rioja': _('La Rioja'),
    'Total': _('Total')
}

COUNTRIES = {
    'Andorra': _('Andorra'),
    'United Arab Emirates': _('United Arab Emirates'),
    'Afghanistan': _('Afghanistan'),
    'Antigua and Barbuda': _('Antigua and Barbuda'),
    'Anguilla': _('Anguilla'),
    'Albania': _('Albania'),
    'Armenia': _('Armenia'),
    'Angola': _('Angola'),
    'Antarctica': _('Antarctica'),
    'Argentina': _('Argentina'),
    'American Samoa': _('American Samoa'),
    'Austria': _('Austria'),
    'Australia': _('Australia'),
    'Aruba': _('Aruba'),
    'Åland Islands': _('Åland Islands'),
    'Azerbaijan': _('Azerbaijan'),
    'Bosnia and Herzegovina': _('Bosnia and Herzegovina'),
    'Barbados': _('Barbados'),
    'Bangladesh': _('Bangladesh'),
    'Belgium': _('Belgium'),
    'Burkina Faso': _('Burkina Faso'),
    'Bulgaria': _('Bulgaria'),
    'Bahrain': _('Bahrain'),
    'Burundi': _('Burundi'),
    'Benin': _('Benin'),
    'Saint Barthélemy': _('Saint Barthélemy'),
    'Bermuda': _('Bermuda'),
    'Brunei': _('Brunei'),
    'Bolivia': _('Bolivia'),
    'Bonaire, Sint Eustatius and Saba': _('Bonaire, Sint Eustatius and Saba'),
    'Brazil': _('Brazil'),
    'Bahamas': _('Bahamas'),
    'Bhutan': _('Bhutan'),
    'Bouvet Island': _('Bouvet Island'),
    'Botswana': _('Botswana'),
    'Belarus': _('Belarus'),
    'Belize': _('Belize'),
    'Canada': _('Canada'),
    'Cocos (Keeling) Islands': _('Cocos (Keeling) Islands'),
    'Congo (Kinshasa)': _('Congo (Kinshasa)'),
    'Central African Republic': _('Central African Republic'),
    'Congo (Brazzaville)': _('Congo (Brazzaville)'),
    'Switzerland': _('Switzerland'),
    'Cote d\'Ivoire': _('Cote d\'Ivoire'),
    'Cook Islands': _('Cook Islands'),
    'Chile': _('Chile'),
    'Cameroon': _('Cameroon'),
    'China': _('China'),
    'Colombia': _('Colombia'),
    'Costa Rica': _('Costa Rica'),
    'Cuba': _('Cuba'),
    'Cabo Verde': _('Cabo Verde'),
    'Curaçao': _('Curaçao'),
    'Christmas Island': _('Christmas Island'),
    'Cyprus': _('Cyprus'),
    'Czechia': _('Czechia'),
    'Germany': _('Germany'),
    'Djibouti': _('Djibouti'),
    'Denmark': _('Denmark'),
    'Dominica': _('Dominica'),
    'Dominican Republic': _('Dominican Republic'),
    'Cruise Ship': _('Cruise Ship'),
    'Algeria': _('Algeria'),
    'Ecuador': _('Ecuador'),
    'Estonia': _('Estonia'),
    'Egypt': _('Egypt'),
    'Western Sahara': _('Western Sahara'),
    'Eritrea': _('Eritrea'),
    'Spain': _('Spain'),
    'Ethiopia': _('Ethiopia'),
    'European Union': _('European Union'),
    'Finland': _('Finland'),
    'Fiji': _('Fiji'),
    'Falkland Islands (Malvinas)': _('Falkland Islands (Malvinas)'),
    'Micronesia': _('Micronesia'),
    'Faroe Islands': _('Faroe Islands'),
    'France': _('France'),
    'Gabon': _('Gabon'),
    'United Kingdom': _('United Kingdom'),
    'Grenada': _('Grenada'),
    'Georgia': _('Georgia'),
    'French Guiana': _('French Guiana'),
    'Guernsey': _('Guernsey'),
    'Ghana': _('Ghana'),
    'Gibraltar': _('Gibraltar'),
    'Greenland': _('Greenland'),
    'Gambia': _('Gambia'),
    'Guinea': _('Guinea'),
    'Guadeloupe': _('Guadeloupe'),
    'Equatorial Guinea': _('Equatorial Guinea'),
    'Greece': _('Greece'),
    'South Georgia': _('South Georgia'),
    'Guatemala': _('Guatemala'),
    'Guam': _('Guam'),
    'Guinea-Bissau': _('Guinea-Bissau'),
    'Guyana': _('Guyana'),
    'Hong Kong': _('Hong Kong'),
    'Heard Island and Mcdonald Islands': _('Heard Island and Mcdonald Islands'),
    'Honduras': _('Honduras'),
    'Croatia': _('Croatia'),
    'Haiti': _('Haiti'),
    'Hungary': _('Hungary'),
    'Indonesia': _('Indonesia'),
    'Ireland': _('Ireland'),
    'Israel': _('Israel'),
    'Isle of Man': _('Isle of Man'),
    'India': _('India'),
    'British Indian Ocean Territory': _('British Indian Ocean Territory'),
    'Iraq': _('Iraq'),
    'Iran': _('Iran'),
    'Iceland': _('Iceland'),
    'Italy': _('Italy'),
    'Jersey': _('Jersey'),
    'Jamaica': _('Jamaica'),
    'Jordan': _('Jordan'),
    'Japan': _('Japan'),
    'Kenya': _('Kenya'),
    'Kyrgyzstan': _('Kyrgyzstan'),
    'Cambodia': _('Cambodia'),
    'Kiribati': _('Kiribati'),
    'Comoros': _('Comoros'),
    'Saint Kitts and Nevis': _('Saint Kitts and Nevis'),
    'North Korea': _('North Korea'),
    'South Korea': _('South Korea'),
    'Kuwait': _('Kuwait'),
    'Cayman Islands': _('Cayman Islands'),
    'Kazakhstan': _('Kazakhstan'),
    'Laos': _('Laos'),
    'Lebanon': _('Lebanon'),
    'Saint Lucia': _('Saint Lucia'),
    'Liechtenstein': _('Liechtenstein'),
    'Sri Lanka': _('Sri Lanka'),
    'Liberia': _('Liberia'),
    'Lesotho': _('Lesotho'),
    'Lithuania': _('Lithuania'),
    'Luxembourg': _('Luxembourg'),
    'Latvia': _('Latvia'),
    'Libya': _('Libya'),
    'Morocco': _('Morocco'),
    'Monaco': _('Monaco'),
    'Moldova': _('Moldova'),
    'Montenegro': _('Montenegro'),
    'Saint Martin (French Part)': _('Saint Martin (French Part)'),
    'Madagascar': _('Madagascar'),
    'Marshall Islands': _('Marshall Islands'),
    'North Macedonia': _('North Macedonia'),
    'Mali': _('Mali'),
    'Myanmar': _('Myanmar'),
    'Mongolia': _('Mongolia'),
    'Macao': _('Macao'),
    'Northern Mariana Islands': _('Northern Mariana Islands'),
    'Martinique': _('Martinique'),
    'Mauritania': _('Mauritania'),
    'Montserrat': _('Montserrat'),
    'Malta': _('Malta'),
    'Mauritius': _('Mauritius'),
    'Maldives': _('Maldives'),
    'Malawi': _('Malawi'),
    'Mexico': _('Mexico'),
    'Malaysia': _('Malaysia'),
    'Mozambique': _('Mozambique'),
    'Namibia': _('Namibia'),
    'New Caledonia': _('New Caledonia'),
    'Niger': _('Niger'),
    'Norfolk Island': _('Norfolk Island'),
    'Nigeria': _('Nigeria'),
    'Nicaragua': _('Nicaragua'),
    'Netherlands': _('Netherlands'),
    'Norway': _('Norway'),
    'Nepal': _('Nepal'),
    'Nauru': _('Nauru'),
    'Niue': _('Niue'),
    'New Zealand': _('New Zealand'),
    'Oman': _('Oman'),
    'Panama': _('Panama'),
    'Peru': _('Peru'),
    'French Polynesia': _('French Polynesia'),
    'Papua New Guinea': _('Papua New Guinea'),
    'Philippines': _('Philippines'),
    'Pakistan': _('Pakistan'),
    'Poland': _('Poland'),
    'Saint Pierre and Miquelon': _('Saint Pierre and Miquelon'),
    'Pitcairn': _('Pitcairn'),
    'Puerto Rico': _('Puerto Rico'),
    'Palestine': _('Palestine'),
    'Portugal': _('Portugal'),
    'Palau': _('Palau'),
    'Paraguay': _('Paraguay'),
    'Qatar': _('Qatar'),
    'Réunion': _('Réunion'),
    'Romania': _('Romania'),
    'Serbia': _('Serbia'),
    'Russia': _('Russia'),
    'Rwanda': _('Rwanda'),
    'Saudi Arabia': _('Saudi Arabia'),
    'Solomon Islands': _('Solomon Islands'),
    'Seychelles': _('Seychelles'),
    'Sudan': _('Sudan'),
    'Sweden': _('Sweden'),
    'Singapore': _('Singapore'),
    'Saint Helena, Ascension and Tristan Da Cunha': _('Saint Helena, Ascension and Tristan Da Cunha'),
    'Slovenia': _('Slovenia'),
    'Svalbard and Jan Mayen': _('Svalbard and Jan Mayen'),
    'Slovakia': _('Slovakia'),
    'Sierra Leone': _('Sierra Leone'),
    'San Marino': _('San Marino'),
    'Senegal': _('Senegal'),
    'Somalia': _('Somalia'),
    'Suriname': _('Suriname'),
    'South Sudan': _('South Sudan'),
    'Sao Tome and Principe': _('Sao Tome and Principe'),
    'El Salvador': _('El Salvador'),
    'Sint Maarten (Dutch Part)': _('Sint Maarten (Dutch Part)'),
    'Syria': _('Syria'),
    'Eswatini': _('Eswatini'),
    'Turks and Caicos Islands': _('Turks and Caicos Islands'),
    'Chad': _('Chad'),
    'French Southern Territories': _('French Southern Territories'),
    'Togo': _('Togo'),
    'Thailand': _('Thailand'),
    'Tajikistan': _('Tajikistan'),
    'Tokelau': _('Tokelau'),
    'Timor-Leste': _('Timor-Leste'),
    'Turkmenistan': _('Turkmenistan'),
    'Tunisia': _('Tunisia'),
    'Tonga': _('Tonga'),
    'Turkey': _('Turkey'),
    'Trinidad and Tobago': _('Trinidad and Tobago'),
    'Tuvalu': _('Tuvalu'),
    'Taiwan*': _('Taiwan*'),
    'Tanzania': _('Tanzania'),
    'Ukraine': _('Ukraine'),
    'Uganda': _('Uganda'),
    'United States Minor Outlying Islands': _('United States Minor Outlying Islands'),
    'United States of America': _('United States of America'),
    'Uruguay': _('Uruguay'),
    'Uzbekistan': _('Uzbekistan'),
    'Holy See': _('Holy See'),
    'Saint Vincent and the Grenadines': _('Saint Vincent and the Grenadines'),
    'Venezuela': _('Venezuela'),
    'Virgin Islands, British': _('Virgin Islands, British'),
    'Virgin Islands, U.S.': _('Virgin Islands, U.S.'),
    'Vietnam': _('Vietnam'),
    'Vanuatu': _('Vanuatu'),
    'Wallis and Futuna': _('Wallis and Futuna'),
    'Samoa': _('Samoa'),
    'Kosovo': _('Kosovo'),
    'Yemen': _('Yemen'),
    'Mayotte': _('Mayotte'),
    'South Africa': _('South Africa'),
    'Zambia': _('Zambia'),
    'Zimbabwe': _('Zimbabwe'),
    'Global': _('Global'),
    'MS Zaandam': _('MS Zaandam')
}
