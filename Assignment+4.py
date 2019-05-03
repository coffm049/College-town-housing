
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[1]:


import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[2]:


# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[3]:


def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    df = pd.read_csv('university_towns.txt', sep = '\n', header= None)
    df.columns = ['RegionName']
    df.loc[:, 'RegionName'] = df.RegionName.map(lambda x: x.split('[')[0])
    df.loc[:, 'RegionName'] = df.RegionName.map(lambda x: x.split('(')[0])
    new_col = []
    
    for name in df['RegionName'] :
        if name in states.values() :
            statename = name 
            df = df.drop(df[df['RegionName'] == statename].index)
        else :
            new_col += [statename]
    df['State'] = new_col
    return df
df = get_list_of_university_towns()


# In[5]:


gdp1 = pd.read_excel('gdplev.xls', skiprows=5, skipfooter=191, usecols= [0,1,2])
gdp1 = gdp1.drop([0, 1])
gdp1['Unnamed: 0'] = gdp1['Unnamed: 0'].astype(int)
gdp1.columns = ['Year', 'GDP current ($)', 'GDP chained 2009 ($)']
gdp1 = gdp1.set_index('Year')


# In[6]:


gdp2 = pd.read_excel('gdplev.xls', skiprows= 5, usecols= [4,5,6])
gdp2 = gdp2.drop([0,1])
gdp2.columns = ['Quarter', 'GDP current ($)', 'GDP 2009 chained ($)']
gdp2 = gdp2.set_index('Quarter')


# In[7]:


pos_begin = []
for i in range(2, len(gdp2['GDP 2009 chained ($)'])) :
    if gdp2['GDP 2009 chained ($)'][i-2] > gdp2['GDP 2009 chained ($)'][i-1] and gdp2['GDP 2009 chained ($)'][i-1] > gdp2['GDP 2009 chained ($)'][i] :
        pos_begin += [gdp2.index[i-2]]
        
pos_end = []
for i in range(2, len(gdp2['GDP 2009 chained ($)'])) :
    if gdp2['GDP 2009 chained ($)'][i-2] < gdp2['GDP 2009 chained ($)'][i-1] and gdp2['GDP 2009 chained ($)'][i-1] < gdp2['GDP 2009 chained ($)'][i] :
        pos_end += [gdp2.index[i]]


# In[8]:


begin_temp = np.array(pos_begin)
end_temp = np.array(pos_end)
rec = []
def identify_recessions (b, e, x) :
    '''Finds the beginning and end of each period of recession. It takes the first item on the identified list of
    possible beginnings of recession and finds the corresponding ending by searching the list of possible endings
    for the first value greater than the beginning. Then it computes this recursively by returning the temporary 
    after removing all possible starts and ends. It outputs a list of tuples the first value of which corresponds
    to the beginning of an identified recession, the second corresponding to the ending of an identified 
    recession.'''
    
    begin_temp = b
    end_temp = e
    if len(begin_temp) != 0 :
        begin = begin_temp[0]
        end = end_temp[end_temp > begin][0]
        x += [(begin, end)]
        return identify_recessions(begin_temp[begin_temp > end], end_temp[end_temp > end], x) 
        
identify_recessions(begin_temp, end_temp, x= rec)
print(rec)


# In[9]:


temp = []
def get_recession_start(t):
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    
    for item in rec :
        t += [item[0]]
    return t
starts = get_recession_start(temp)


# In[10]:


temp = []
def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    
    for item in rec :
        t += [item[1]]
    return t


# In[11]:



def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    
    bottoms = []
    for r in rec :
        low = gdp2['GDP 2009 chained ($)'].loc[r[0]:r[1]].min()
        ye = gdp2[gdp2['GDP 2009 chained ($)'] == low].index
        bottoms += [ye]
    return bottoms
bots = get_recession_bottom()


# In[12]:


homes = pd.read_csv('City_Zhvi_AllHomes.csv')
new_col = []
for col in homes.columns :
    if '-' in col :
        if col.split('-')[1] in ['01', '02', '03'] :
            new_col += [col.split('-')[0] + 'q1']
        elif col.split('-')[1] in ['04', '05', '06'] :
            new_col += [col.split('-')[0] + 'q2']
        elif col.split('-')[1] in ['07', '08', '09'] :
            new_col += [col.split('-')[0] + 'q3']
        elif col.split('-')[1] in ['10', '11', '12'] :
            new_col += [col.split('-')[0] + 'q4']
    else :
        new_col += [col]
        
homes.columns = new_col


# In[13]:


qs = []
for col in homes.columns :
    if 'q' in col :
        qs += [col]
        
justyears = homes[qs]


# In[ ]:


def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    quartersagg = justyears.T.groupby(level= 0).agg('mean').T
    after2000 = quartersagg[np.array(quartersagg.columns)[np.array(quartersagg.columns) > '1999q5']]
    houses_small = homes[list(homes.columns[0:6])]
    houses_combo = houses_small.merge(after2000, 'inner', left_index = True, right_index = True)
    for i, abb in enumerate(houses_combo['State']) :
        houses_combo['State'][i] = states[abb]
    houses_combo = houses_combo.set_index(['State', 'RegionName'])
    return houses_combo

house_combo = convert_housing_data_to_quarters()


# In[ ]:


starts_2000 = np.array(starts)[np.array(starts) > '1999q5']
bots_2000 = np.array(bots)[np.array(bots) > '1999q5']


# In[ ]:


print(bots_2000[0])


# In[ ]:


df = df.set_index(['State', 'RegionName'])


# In[ ]:


from scipy import stats
houses_combo['drop'] = houses_combo[bots_2000[0]] - houses_combo[starts_2000[0]]



def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    
    
    
    return "ANSWER"


# In[ ]:


houses_combo.loc[:, 'College town?'] = df.RegionName.map(lambda x: x in list(df['RegionName'])
houses_groupby('College town?').agg('mean')

