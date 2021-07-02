import pandas as pd
import plotly.graph_objs as go

# read in and wrangle data and prepare plotly visualizations

def wrangle_data(data_path):
    """Reads in an cleans data needed for visualizations.
    For more information on the wrangling process, see Juypter notebook of this
    project: github.com/zoraaroz/global-fertility-rate

    Args:
        data_path (string): name of folder containing .csv-files

    Returns:
        df_fertility, df_mortality, df_income, df_edu, df_urban: data frames
        containing data used for visualizations

    """
    # 0. read in data
    df_fertility_raw = pd.read_csv(data_path + '/fertility.csv')
    df_mortality_raw = pd.read_csv(data_path + '/child_mortality.csv')
    df_income_raw = pd.read_csv(data_path + '/income_per_person.csv')
    df_edu_raw = pd.read_csv(data_path + '/education.csv')
    df_urban_raw = pd.read_csv(data_path + '/urban_population.csv')
    df_geo_raw = pd.read_csv(data_path + '/country_regions.csv',sep=';')

    # 1. drop years later than 2020 in the respective data frames
    df_fertility_2020 = df_fertility_raw.drop(df_fertility_raw.columns[222:],axis=1)
    df_mortality_2020 = df_mortality_raw.drop(df_mortality_raw.columns[222:],axis=1)
    df_income_2020 = df_income_raw.drop(df_income_raw.columns[222:],axis=1)

    # 2. re-write geography data frame, only keeping country and eight_regions
    df_geo_large = df_geo_raw[['name','four_regions']]
    df_geo_large = df_geo_large.rename(columns={'name':'country'})

    # 3a. define function for merging
    def country_merge(df_1,df_2):
        df_merged = pd.merge(df_1, df_2, on="country", how="inner")
        return df_merged

    # 3b. merge data frames with region categories
    df_fertility_cat = country_merge(df_geo_large, df_fertility_2020)
    df_mortality_cat = country_merge(df_geo_large, df_mortality_2020)
    df_income_cat = country_merge(df_geo_large, df_income_2020)
    df_edu_cat = country_merge(df_geo_large, df_edu_raw)
    df_urban_cat = country_merge(df_geo_large, df_urban_raw)

    # 4a. make sure the same countries are used in all data frames
    df_geo_1 = country_merge(df_geo_large, df_fertility_cat.country)
    df_geo_2 = country_merge(df_geo_1, df_mortality_cat.country)
    df_geo_3 = country_merge(df_geo_2, df_income_cat.country)
    df_geo_4 = country_merge(df_geo_3, df_edu_cat.country)
    df_geo = country_merge(df_geo_4, df_urban_cat.country)

    # 4b. filter data and reset each index
    countries = df_geo.country
    df_fertility = df_fertility_cat[df_fertility_cat.country.isin(countries)].reset_index(drop=True)
    df_mortality = df_mortality_cat[df_mortality_cat.country.isin(countries)].reset_index(drop=True)
    df_income = df_income_cat[df_income_cat.country.isin(countries)].reset_index(drop=True)
    df_edu = df_edu_cat[df_edu_cat.country.isin(countries)].reset_index(drop=True)
    df_urban = df_urban_cat[df_urban_cat.country.isin(countries)].reset_index(drop=True)

    return df_fertility, df_mortality, df_income, df_edu, df_urban, df_geo


def return_figures():
    """Creates plotly visualizations

    Args:
        None

    Returns:
        list (dict): list containing plotly visualizations

    """
    df_fertility, df_mortality, df_income, df_edu, df_urban, df_geo = wrangle_data('data')

    # first chart
    graph_one = []
    for r in df_geo['four_regions'].unique():
        graph_one.append(
          go.Scatter(
          x = df_fertility.columns.tolist(),
          y = df_fertility.groupby('four_regions').mean().loc[r],
          mode = 'lines',
          name = r))

    graph_one.append(
        go.Scatter(
        x = df_fertility.columns.tolist(),
        y = df_fertility.mean(),
        mode = 'lines',
        name = 'global mean',
        line = dict(color = 'black', width = 3)))

    layout_one = dict(title = 'Fertility rate in the past 220 years',
                xaxis = dict(title = 'Year'),
                yaxis = dict(title = 'Number of children per woman'))

    # second chart
    graph_two = []
    graph_two.append(go.Histogram(
                        x = df_fertility['1800'],
                        name = '1800',
                        opacity = .6))
    graph_two.append(go.Histogram(
                        x = df_fertility['2020'],
                        name = '2020',
                        opacity = .6))

    layout_two = dict(title = 'Global fertility rate in 1800 and today',
                barmode = 'overlay',
                xaxis = dict(title = 'Number of children per woman',),
                yaxis = dict(title = 'Count'))

    # third chart
    year_list = ['1800','1910','1965','2020']
    x = df_fertility

    graph_three = []
    for year in year_list:
        r = x.corrwith(df_mortality[year])[year]
        graph_three.append(
          go.Scatter(x = x[year], y = df_mortality[year],
          mode = 'markers', name = '{}, r = {}'.format(year, round(r,2)),
          opacity = .6))

    layout_three = dict(title = 'Fertility rate vs. child mortality',
                xaxis = dict(title = 'Number of children per woman'),
                yaxis = dict(title = 'Child deaths / 1000 births'))

    # fourth chart
    graph_four = []
    for year in year_list:
        r = x.corrwith(df_income[year])[year]
        graph_four.append(go.Scatter(x = x[year], y = df_income[year],
        mode = 'markers', name = '{}, r = {}'.format(year, round(r,2)),
        opacity = .6))

    layout_four = dict(title = 'Fertility rate vs. income per person',
                xaxis = dict(title = 'Number of children per woman'),
                yaxis = dict(title = 'Income [$] (logarithmic)', type = 'log'))

    # fifth chart
    year_list = ['1970','1990','2009']
    graph_five = []
    for year in year_list:
        r = x.corrwith(df_edu[year])[year]
        graph_five.append(
          go.Scatter(x = x[year], y = df_edu[year],
          mode = 'markers', name = '{}, r = {}'.format(year, round(r,2)),
          opacity = .6))

    layout_five = dict(title = 'Fertility rate vs. female education',
                xaxis = dict(title = 'Number of children per woman'),
                yaxis = dict(title = 'Years of education'))

    # sixth chart
    year_list = ['1960','1990','2019']
    graph_six = []
    for year in year_list:
        r = x.corrwith(df_urban[year])[year]
        graph_six.append(
          go.Scatter(x = x[year], y = df_urban[year],
          mode = 'markers', name = '{}, r = {}'.format(year, round(r,2)),
          opacity = .6))

    layout_six = dict(title = 'Fertility rate vs. urbanity',
                xaxis = dict(title = 'Number of children per woman'),
                yaxis = dict(title = 'People living in urban areas [%]'))


    # append all charts to the figures list
    figures = []
    figures.append(dict(data=graph_one, layout=layout_one))
    figures.append(dict(data=graph_two, layout=layout_two))
    figures.append(dict(data=graph_three, layout=layout_three))
    figures.append(dict(data=graph_four, layout=layout_four))
    figures.append(dict(data=graph_five, layout=layout_five))
    figures.append(dict(data=graph_six, layout=layout_six))

    return figures
