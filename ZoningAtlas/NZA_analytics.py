## IMPORTS

import os
import numpy as np
import pandas as pd
import matplotlib as mpl
from matplotlib import pyplot as plt
import geopandas as gpd
import warnings # To suppress warning displays in console output


## FUNCTION DECLARATION

def consolidate_data(folder, gis_or_zoning): # gis_or_zoning is a string variable with value of either 'gis' or 'zoning'
    counter = 0
    base_dir = os.path.join(os.getcwd(), folder)
    for gjson in os.listdir(base_dir):
        thisfile = gjson
        if thisfile !='.DS_Store':
            f = os.path.join(base_dir, thisfile)
            with open(f, 'r') as filename:
                if gis_or_zoning == 'gis':
                    this_jxtn = load_gis(f)
                else:
                    if gis_or_zoning == 'zoning':
                        this_jxtn = load_zoning(filename)
                    else:
                        print('Need to specify type of dataframe')
                        return(-1)
                if counter == 0:
                    all_VT_zoning = this_jxtn
                    counter = 1
                else:
                    all_VT_zoning = pd.concat([this_jxtn, all_VT_zoning])
            filename.close()
        print(str(gjson), gis_or_zoning, 'consolidated.')
    all_VT_zoning=all_VT_zoning.reset_index(drop = True)
    return all_VT_zoning

def load_gis(filename):
    gdf = gpd.read_file(filename)
    gdf = get_areas(gdf)
    return gdf

def load_zoning(filename): # can be used to load .csv of either jurisdiction or district data
    df = pd.read_csv(filename)
    return df

def get_areas(gdf):
    gdf_copy = gdf.copy()
    gdf_copy = gdf_copy.to_crs('epsg:3083')
    gdf_copy['area'] = gdf_copy.geometry.area
    gdf_copy['area'] = gdf_copy['area']*3.86102*10**(-7)
    return gdf_copy

def get_total_area(gdf):
    base_districts = gdf.loc[gdf['Overlay'] == 'No']
    return(round(sum(base_districts['area']), 1))

def slice_gdf(var, gdf, slice_label):
    slice_gdf = gdf.loc[gdf[var] == slice_label]
    return slice_gdf

def fxn():
    warnings.warn("deprecated", DeprecationWarning)

def percent_coverage(gdf, attribute, value):
    gdf_copy = gdf.copy()
    if type(value) != list:
        gdf_att_true = gdf_copy.loc[(gdf_copy[attribute] == value) & (gdf_copy['Overlay'] == 'No')]
    else:
        gdf_att_true = gdf_copy.loc[(gdf_copy[attribute].isin(value)) & (gdf_copy['Overlay']== 'No')]
    area_true = sum(gdf_att_true['area'])
    all_area = get_total_area(gdf)
    return round(100*area_true/all_area, 1)

def viz_allvals(gdf,attr):
    gdf_copy = gdf.copy()
    fig, ax = plt.subplots()
    gdf_copy.sort_values(attr, inplace = True)
    cmap = (mpl.colors.ListedColormap(['purple', 'black', 'orange', 'lightgray', 'green']))
    gdf_copy[attr].replace("", 'Unspecified', inplace=True)
    gdf_copy = gdf_copy.loc[gdf_copy['Overlay'] == 'No']
    gdf_copy.plot(column=attr, categorical=True, ax=ax, cmap=cmap, legend=True)
    starty = 0.1
    counter = 0
    for value in gdf_copy[attr].unique():
        if value != 'Overlay' and value != 'Unspecified':
            plt.figtext(0.02, starty - 0.025 * counter, attr + ' ' + value + ' in '
                        + str(percent_coverage(gdf_copy, attr, value))
                        + '% of land area.')
            counter += 1
    plt.title(attr + ' Distribution in \nAddison and Chittenden Counties, VT')
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig('imgs/full_distr_'+attr.lower().strip(' ')+'.jpg')
    plt.clf()

def viz_binary_val(gdf,attr,targetval):
    gdf_copy = gdf.copy()
    fig, ax = plt.subplots()
    cmap = (mpl.colors.ListedColormap(['purple', 'lightgray']))
    for val in gdf_copy[attr].unique():
        if val != targetval:
            gdf_copy[attr].replace(val, 'ZZZ', inplace=True)
    gdf_copy = gdf_copy.loc[gdf_copy['Overlay'] == 'No']
    gdf_copy.sort_values(attr)
    gdf_copy.plot(column=attr, categorical=True, ax=ax, cmap=cmap)
    starty = 0.1
    plt.figtext(0.02, 0.1, attr + ' '+ targetval + ' in '
                + str(percent_coverage(gdf_copy, attr, targetval))
                + '% of land area.')
    plt.figtext(0.02, starty - 0.025, attr + ' not ' + targetval + ' in '
                + str(round(100 - percent_coverage(gdf_copy, attr, targetval), 1))
                + '% of land area.')
    plt.title('Base districts where ' + attr + ' is ' + targetval + '\nAddison and Chittenden Counties, VT')
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig('imgs/binary_val_'+attr.lower().strip(' ')+'.jpg')
    plt.clf()

def barplot_res_tx(gdf, targetvals, title):
    xlabels = []
    heights = []
    for x in ['1', '2', '3', '4+']:
        attr = x + '-Family Treatment'
        heights.append(percent_coverage(gdf, attr, targetvals))
        xlabels.append(attr)
    plt.bar(xlabels, heights)
    plt.title(title)
    plt.tight_layout()
    if type(targetvals) == list:
        filename = str([x.replace('/', '_') for x in targetvals])
    else:
        filename = targetvals.replace('/', '_')
    plt.savefig('imgs/barplot_' + filename + '.jpg')
    plt.clf()

def lot_size(gdf, att, minlotsize, max_or_min):
    gdf_copy = gdf.copy()
    min_or_max_size = pd.DataFrame(columns = gdf_copy.columns)
    no_min_or_max_size = pd.DataFrame(columns = gdf_copy.columns)
    for index, row in gdf_copy.iterrows():
        try:
            if float(row[att]) > minlotsize and max_or_min == 'min':
                min_or_max_size.loc[len(min_or_max_size)] = row
            else:
                if float(row[att]) < minlotsize and max_or_min == 'max':
                    min_or_max_size.loc[len(min_or_max_size)] = row
        except:
            no_min_or_max_size.loc[len(no_min_or_max_size)] = row
    if max_or_min == "neither":
        return round(100*sum(no_min_or_max_size['area'])/sum(gdf_copy['area']), 2)
    else:
        return round(100*sum(min_or_max_size['area'])/sum(gdf_copy['area']), 2)

## MAIN CODE RETURNING ANALYTICS REQUESTED BY NATIONAL ZONING ATLAS

plt.rcParams["figure.figsize"] = [15, 15]

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    fxn()

print('\nCREATING FILES\n')

# Set global coordinate reference system variable to initialize all geoDataFrames
crs = {'init': 'epsg:4326'}

# Check to see if consolidated datasets exist for district and jurisdictional zoning and geospatial files
# For each: if yes, then read file to object in current workspace
# If no, load data for all districts in directory into a single GeoDataFrame

if (os.path.exists("consolidated/district_geodata.geojson") == False):
    all_district_geodata = consolidate_data('districts_gis', 'gis')
    all_district_geodata.to_json()
    all_district_geodata.to_file('consolidated/district_geodata.geojson')
    print('Consolidated district geodata created.')
else:
    print('Consolidated district geodata exists.')
    all_district_geodata = gpd.read_file("consolidated/district_geodata.geojson")

if(os.path.exists('consolidated/district_zoning_data.csv') == False):
    all_district_zoning_data = pd.DataFrame(all_district_geodata, copy = True).drop(columns = ['geometry','area'])
    all_district_zoning_data.to_csv('consolidated/district_zoning_data.csv')
    print('Consolidated district zoning data created.')
else:
    print('Consolidated district zoning data exists.')
    all_district_zoning_data = pd.read_csv('consolidated/district_zoning_data.csv')

if (os.path.exists('consolidated/jxtn_data.csv') == False):
    all_jxtn_data = consolidate_data('jxtns', 'zoning')
    all_jxtn_data.to_csv('consolidated/jxtn_data.csv')
else:
    print('Consolidated jurisdiction attribute data exists.')
    all_jxtn_data = pd.read_csv('consolidated/jxtn_data.csv')

if (os.path.exists('consolidated/jxtn_footprints.geojson')) == False:
    all_jxtn_footprints = consolidate_data('jxtn_footprints', 'gis')
    all_jxtn_footprints.to_json()
    all_jxtn_footprints.to_file('consolidated/jxtn_footprints.geojson')
    print('Consolidated jurisdiction footprint data created.')
else:
    print('Consolidated jursidictional footprint data exists.')
    all_jxtn_footprints = gpd.read_file('consolidated/jxtn_footprints.geojson')

# Creates tracking list of all districts complete to date for project management purposes
all_district_geodata[['Jurisdiction', 'County', 'Full District Name']].to_csv('tracking_list.csv')

# Can be used to limit data to a single county or subset of counties
# all_district_geodata = all_district_geodata.loc[all_district_geodata['County'] == 'Addison County']
# all_jxtn_data = all_jxtn_data.loc[all_jxtn_data['County'] == 'Addison County']

''' Jurisdiction characteristics '''

print('\nJURISDICTION CHARACTERISTICS')

# Total number of jurisdictions analyzed
print('\nTotal number of jurisdictions analyzed')
print('------------------------------------------')
print('Total number of jurisdictions analyzed: ', len(all_jxtn_data))
print('Total number of districts analyzed: ', len(all_district_zoning_data))
print('Total number of geospatial files completed: ', len(all_district_geodata))

# Side-by-side barplot of jurisdiction types both with and without zoning
govt_types = all_jxtn_data.groupby(['Type of Government', 'Does It Have Zoning?']).size().reset_index(name='count')
xlabels = []
heights = []
for index, row in govt_types.iterrows():
    if govt_types.loc[index]['Does It Have Zoning?'] == 'Yes':
        zoninglabel = ' With Zoning'
    elif govt_types.loc[index]['Does It Have Zoning?'] == 'No':
        zoninglabel = ' Without Zoning'
    xlabels.append(govt_types.loc[index]['Type of Government'] + '\n' + zoninglabel)
    heights.append(govt_types.loc[index]['count'])

plt.bar(xlabels, heights)
plt.title('Types of Jurisdictional Government in Dataset')
plt.tight_layout()
plt.savefig('imgs/barplot_zoning_or_no.jpg')
plt.clf()

# Number and percentage of jurisdictions with zoning
print('\nPresence of zoning')
print('----------------------')
print('Number of jurisdictions with zoning: ', all_jxtn_data['Does It Have Zoning?'].value_counts()['Yes'])
print('Percentage of jurisdictions with zoning: ', all_jxtn_data['Does It Have Zoning?'].value_counts()['Yes']/len(all_jxtn_data))

# Map zoned versus unzoned districts
cmap = (mpl.colors.ListedColormap(['lightgray', 'green']))
all_jxtn_footprints.plot(column = 'Does It Have Zoning?', categorical=True, cmap=cmap, legend=True, legend_kwds={'labels': ['Unzoned', 'Zoned']})
all_jxtn_area = sum(all_jxtn_footprints['area'])
all_zoned_jxtns = sum(all_jxtn_footprints.loc[all_jxtn_footprints['Does It Have Zoning?'] == 'Yes']['area'])
plt.title('Addison and Chittenden County Jurisdictions, VT')
plt.figtext(0.02, 0.1, str(round(100*all_zoned_jxtns/all_jxtn_area, 1)) + '% of analyzed area is zoned.')
plt.axis('off')
plt.savefig('imgs/map_zoned_or_no.jpg')
plt.clf()

# Total # pages of zoning text analyzed
print('\nZoning Text Length')
print('----------------------')
all_jxtn_footprints['# of Pages in the Zoning Code'].astype(int, copy = False)
print('Total number of pages of zoning text analyzed: ', np.sum(all_jxtn_footprints['# of Pages in the Zoning Code']))

# Average # pages in each zoning text
print('Average number of pages per zoning text: ', round(np.average(all_jxtn_footprints['# of Pages in the Zoning Code']), 1))

# Shortest and longest texts
minpages = np.min(all_jxtn_footprints.loc[all_jxtn_footprints['# of Pages in the Zoning Code']!=0]['# of Pages in the Zoning Code'])
print('Shortest zoning text: ', str(minpages) + ' pages\nJurisdiction(s):', str(all_jxtn_data.loc[all_jxtn_footprints['# of Pages in the Zoning Code'] == minpages]['Jurisdiction']))
maxpages = np.max(all_jxtn_footprints['# of Pages in the Zoning Code'])
print('Longest zoning text: ', str(maxpages) + ' pages\nJurisdiction(s):', str(all_jxtn_footprints.loc[all_jxtn_footprints['# of Pages in the Zoning Code'] == maxpages]['Jurisdiction']))

# Oldest district analyzed

# Average # of districts per locality
print('\nNumber of districts per locality: ', round(len(all_district_zoning_data)/len(all_district_zoning_data['Jurisdiction'].unique()), 1))

# Total # and % of districts mapped and unmapped

# Calculate areas of all districts in jurisdiction
# Format as table
divider = '----------------------------------------------------------------------'
print('\n')
print('Total area zoned by jurisdiction:'.center(len(divider)))
print(divider)
print('JURISDICTION'.ljust(15), '\tINCLUDING OVERLAYS\tEXCLUDING OVERLAYS')
for jxtn in all_district_geodata['Jurisdiction'].unique():
    thisjxtn = all_district_geodata.loc[all_district_geodata['Jurisdiction'] == jxtn]
    thisjxtn_wo_overlays = get_total_area(thisjxtn)
    print(jxtn.ljust(25), '\t', str(round(sum(all_district_geodata.loc[all_district_geodata['Jurisdiction'] == jxtn]['area']), 1)).ljust(20), thisjxtn_wo_overlays)

''' Zoning characteristics '''

print('\nZONING CHARACTERISTICS')

# Map type of district
viz_allvals(all_district_geodata, 'Type of Zoning District')
viz_binary_val(all_district_geodata, 'Type of Zoning District', 'Primarily Residential')
viz_binary_val(all_district_geodata, 'Type of Zoning District', 'Mixed with Residential')
viz_binary_val(all_district_geodata, 'Type of Zoning District', 'Nonresidential')

# Barplot of % area zoned with each due process requirement value for 1, 2, 3, and 4+ family treatments
barplot_res_tx(all_district_geodata, ['Allowed/Conditional', 'Public Hearing'],
               '% Base District Area Zoned For Residential Treatments,\nAllowed/Conditional or Public Hearing Required'
               '\nChittenden and Addison Counties, VT')
barplot_res_tx(all_district_geodata, 'Allowed/Conditional',
               '% Base District Area Zoned By-Right,\n Chittenden and Addison Counties, VT')
barplot_res_tx(all_district_geodata, 'Public Hearing',
               '% Base District Area Requiring Public Hearing,\n Chittenden and Addison Counties, VT')

# % of land zoned for 1-family housing and no other type of housing
one_fam_only = pd.DataFrame(columns = all_district_geodata.columns)
for index, row in all_district_geodata.iterrows():
    if row['1-Family Treatment'] == 'Allowed/Conditional'or row['1-Family Treatment'] == 'Public Hearing':
        if row['2-Family Treatment'] == 'Prohibited' and row['3-Family Treatment'] == 'Prohibited' \
                and row['4+-Family Treatment'] == 'Prohibited':
            one_fam_only.loc[len(one_fam_only)] = row
print(str(round(100*sum(one_fam_only['area'])/sum(all_district_geodata['area']), 2)), '% of analyzed land zoned solely '
                                                                                      'for 1-family housing')

''' Lot Characteristics '''

print('\nLOT CHARACTERISTICS')
print(str(lot_size(all_district_geodata, '1-Family Min. Lot', 0.46, 'min')), '% of land zoned for 1-Family Treatment '
                                                                          'has minimum lot size > 0.46 acres.')
print(str(lot_size(all_district_geodata, '1-Family Min. Lot', 0.92, 'min')), '% of land zoned for 1-Family Treatment '
                                                                          'has minimum lot size > 0.92 acres.')
print(str(lot_size(all_district_geodata, '1-Family Min. Lot', 1.84, 'min')), '% of land zoned for 1-Family Treatment '
                                                                          'has minimum lot size > 1.84 acres.')

min_lot_size_reqs = [('No minimum requirement', 100 - lot_size(all_district_geodata, '1-Family Min. Lot', 0, 'min')),
                     ('<0.46 ac', lot_size(all_district_geodata, '1-Family Min. Lot', 0, 'min')),
                     ('>0.46 ac', lot_size(all_district_geodata, '1-Family Min. Lot', 0.46, 'min')),
                     ('>0.92 ac', lot_size(all_district_geodata, '1-Family Min. Lot', 0.92, 'min')),
                     ('>1.84 ac', lot_size(all_district_geodata, '1-Family Min. Lot', 1.84, 'min'))]

nominlotsize = lot_size(all_district_geodata, '1-Family Min. Lot', 0, 'neither')
anyminlotsize = lot_size(all_district_geodata, '1-Family Min. Lot', 0, 'min')
greaterthan46 = lot_size(all_district_geodata, '1-Family Min. Lot', 0.46, 'min')
lessthan46 = anyminlotsize-greaterthan46
greaterthan92 = lot_size(all_district_geodata, '1-Family Min. Lot', 0.92, 'min')
greaterthan184 = lot_size(all_district_geodata, '1-Family Min. Lot', 1.84, 'min')

names = ['No minimum ('+ str(round(nominlotsize, 2)) + '%)', '0-0.46 acres (' + str(round(lessthan46, 2))+'%)',
         '0.47-0.92 acres (' +str(round(anyminlotsize - greaterthan92 - lessthan46, 2)) +'%)',
         '0.92-1.84 acres ('+str(round(greaterthan92-greaterthan184, 2))+'%',
         '>1.85 acres (' +str(round(greaterthan184, 2))+'%)']
plt.pie([nominlotsize, lessthan46, anyminlotsize - greaterthan92 - lessthan46,
         greaterthan92-greaterthan184, greaterthan184], labels=names,
        wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' })
my_circle=plt.Circle( (0,0), 0.7, color='white')
p=plt.gcf()
plt.title('Minimum lot size requirements\nChittenden & Addison Counties, VT')
p.gca().add_artist(my_circle)
plt.show()

# Barplot of minimum lot sizes for 1-Family Housing

# Option 1: Stacked barplot
for i in range(5):
    plt.bar(range(1), min_lot_size_reqs[i][1], label = min_lot_size_reqs[i][0])
plt.legend(bbox_to_anchor = (1, 0.5))
plt.tick_params(labelbottom = False, bottom = False)

# Option 2: Traditional barplot
plt.bar(range(5), [x[1] for x in min_lot_size_reqs], color=['green', 'dimgray', 'dimgray', 'dimgray', 'dimgray'])
plt.title('Minimum Lot Size Requirements\nAll Mapped Districts, VT')
plt.xticks(range(5), [x[0] for x in min_lot_size_reqs])
plt.show()

# Map due process requirements for residential treatments
viz_allvals(all_district_geodata, '1-Family Treatment')
viz_allvals(all_district_geodata, '2-Family Treatment')
viz_allvals(all_district_geodata, '3-Family Treatment')
viz_allvals(all_district_geodata, '4+-Family Treatment')
viz_allvals(all_district_geodata, 'Accessory Dwelling Unit (ADU) Treatment')
viz_allvals(all_district_geodata, 'Planned Residential Development (PRD) Treatment')

