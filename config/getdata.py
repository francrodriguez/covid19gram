#!/bin/env python
# -*- coding: utf-8 -*-
import git
import json
import datetime
import pandas as pd
import numpy as np
import os

SCOPES = {
    'world': {
        'base_directory': 'external-data/world',
        'repo_url': 'https://github.com/pomber/covid19.git',
        'watch': [
            'docs/timeseries.json',
        ]
    },
    'spain': {
        'base_directory': 'external-data/spain',
        'repo_url': 'https://github.com/datadista/datasets',
        'watch': [
            'COVID 19/ccaa_covid19_casos_long.csv',
            'COVID 19/ccaa_covid19_altas_long.csv',
            'COVID 19/ccaa_covid19_fallecidos_long.csv',
            # 'COVID 19/ccaa_covid19_hospitalizados_long.csv'
        ]
    },
    'italy': {
        'base_directory': 'external-data/italy',
        'repo_url': 'https://github.com/pcm-dpc/COVID-19',
        'watch': [
            'dati-regioni/dpc-covid19-ita-regioni.csv'
        ]
    },
    'france': {
        'base_directory': 'external-data/france',
        'repo_url': 'https://github.com/opencovid19-fr/data',
        'watch': [
            'dist/chiffres-cles.csv'
        ]
    },
}


def update_data(force=False):
    updated = {}
    for scope in SCOPES.keys():
        updated[scope] = update_scope_data(scope, force=force)
    return updated


def status_data():
    text = "**Data sources updated at:**\n"
    for scope in SCOPES.keys():
        base_directory = SCOPES[scope]['base_directory']
        repo = git.Repo(base_directory)
        headcommit = repo.head.commit
        mtime = datetime.datetime.fromtimestamp(headcommit.committed_date)
        text += f"- {scope}: {mtime:%d %b %Y %H:%M:%S}\n"
    return text


def update_scope_data(scope, data_directory="data/", force=False):
    print("[" + datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] " + "Start update data for " + scope)
    if not repository_has_changes(scope, data_directory) and not force:
        print("[" + datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] " + "Finish update data for " + scope + ". No changes in repository")
        return False
    input_files = get_or_generate_input_files(scope, data_directory)
    generate_covidgram_dataset(scope, input_files, data_directory)
    print("[" + datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] " + "Finish update data for " + scope + ". New file created")
    return True


def get_or_generate_input_files(scope, data_directory="data/"):
    if scope in ['spain', 'italy', 'france']:
        base_directory = SCOPES[scope]['base_directory']
        files = [base_directory + "/" + f for f in SCOPES[scope].get('watch', [])]
        return files

    if scope == 'world':
        generate_world_input_files(data_directory)

    return [
        data_directory + scope + '_cases.csv',
        data_directory + scope + '_recovered.csv',
        data_directory + scope + '_deceased.csv'
    ]


def repository_last_changes(scope):
    base_directory = SCOPES[scope]['base_directory']
    files = [base_directory + "/" + f for f in SCOPES[scope].get('watch', [])]
    files_mtime = []
    for f in files:
        files_mtime.append(int(os.path.getmtime(f)))
    return np.max(files_mtime)


def repository_has_changes(scope, data_directory):
    # check if repository exists
    base_directory = SCOPES[scope]['base_directory']
    if not os.path.exists(base_directory):
        os.makedirs(base_directory)
        git.Repo.clone_from(SCOPES[scope]['repo_url'], base_directory)
        return True
    original_mtime = repository_last_changes(scope)

    # update repository
    g = git.cmd.Git(base_directory)
    try:
        g.pull()
    except git.GitCommandError as e:
        print("Error pulling data from " + scope + ": " + e.stderr)
        try:
            g.reset('--hard', 'origin/master')
            g.pull()
            print("Error solved with reset --hard")
        except git.GitCommandError as e:
            raise e
    # check if files changed
    new_mtime = repository_last_changes(scope)
    if original_mtime != new_mtime:
        return True
    # check if exists covid19gram file for this scope and its mtime
    csv_covid19gram = f"{data_directory}/{scope}_covid19gram.csv"
    if not os.path.isfile(csv_covid19gram):
        return True
    csv_mtime = int(os.path.getmtime(csv_covid19gram))
    if csv_mtime < new_mtime:
        return True
    return False


def generate_world_input_files(data_directory="data/"):
    import_file_path = SCOPES['world']['base_directory'] + "/docs/timeseries.json"
    # generate files cases, recovered and deceased
    with open(import_file_path) as json_file:
        data = json.load(json_file)

    export_cases = data_directory + 'world_cases.csv'
    export_recovered = data_directory + 'world_recovered.csv'
    export_deceased = data_directory + 'world_deceased.csv'

    with open(export_cases, 'w') as cases_file, open(export_recovered, 'w') as recovered_file, open(export_deceased, 'w') as deceased_file:
        cases_file.write("date,region_code,CCAA,total\n")
        recovered_file.write("date,region_code,CCAA,total\n")
        deceased_file.write("date,region_code,CCAA,total\n")

        country_code = 0
        global_cases = {}
        global_recovered = {}
        global_deceased = {}
        for country in data:
            for row in data[country]:
                country_name = country.replace(",", "")
                date = row['date']
                confirmed = row['confirmed']
                recovered = row['recovered']
                deaths = row['deaths']

                # get global data
                if date in global_cases:
                    global_cases[date] += confirmed
                else:
                    global_cases[date] = confirmed
                if date in global_recovered:
                    global_recovered[date] += recovered
                else:
                    global_recovered[date] = recovered
                if date in global_deceased:
                    global_deceased[date] += deaths
                else:
                    global_deceased[date] = deaths

                cases_file.write(
                    f"{date},{country_code},{country_name},{confirmed}\n")
                recovered_file.write(
                    f"{date},{country_code},{country_name},{recovered}\n")
                deceased_file.write(
                    f"{date},{country_code},{country_name},{deaths}\n")
            country_code += 1

        # add global information for each date
        for date in global_cases.keys():
            cases_file.write(
                f"{date},{country_code},total-world,{global_cases[date]}\n")
        for date in global_recovered.keys():
            recovered_file.write(
                f"{date},{country_code},total-world,{global_recovered[date]}\n")
        for date in global_deceased.keys():
            deceased_file.write(
                f"{date},{country_code},total-world,{global_deceased[date]}\n")


def generate_covidgram_dataset(scope, files, data_directory):
    csv_cases = None
    csv_recovered = None
    csv_deceased = None
    csv_hospitalized = None

    if len(files) == 3:
        csv_cases, csv_recovered, csv_deceased = files
    elif len(files) == 4:
        csv_cases, csv_recovered, csv_deceased, csv_hospitalized = files
    else:
        csv_cases = files[0]

    df = pd.read_csv(csv_cases)
    # rename, convert date to datetime and set index
    df.rename(columns={
        'fecha': 'date', 'cod_ine': 'region_code',
        'total': 'cases', 'CCAA': 'region'}, inplace=True)

    # italy: data,stato,codice_regione,denominazione_regione,lat,long,ricoverati_con_sintomi,terapia_intensiva,totale_ospedalizzati,isolamento_domiciliare,totale_positivi,variazione_totale_positivi,nuovi_positivi,dimessi_guariti,deceduti,totale_casi,tamponi,note_it,note_en
    if scope == 'spain':
        df['region'].mask(df.region_code == 0, 'total-spain', inplace=True)
    elif scope == 'italy':
        df.drop(columns=[
            'stato', 'lat', 'long', 'ricoverati_con_sintomi',
            'terapia_intensiva', 'isolamento_domiciliare',
            'totale_positivi', 'variazione_totale_positivi',
            'nuovi_positivi', 'tamponi', 'note_it', 'note_en'], inplace=True)

        df.rename(columns={
            'data': 'date', 'codice_regione': 'region_code',
            'totale_casi': 'cases', 'denominazione_regione': 'region',
            'totale_ospedalizzati': 'hospitalized',
            'dimessi_guariti': 'recovered', 'deceduti': 'deceased'}, inplace=True)
        # avoid duplicates
        df['region_code'].mask(df.region == "P.A. Bolzano", '4A', inplace=True)
        df['region_code'].mask(df.region == "P.A. Trento", '4B', inplace=True)
    elif scope == 'france':
        # france date,granularite,maille_code,maille_nom,cas_confirmes,cas_ehpad,cas_confirmes_ehpad,cas_possibles_ehpad,deces,deces_ehpad,reanimation,hospitalises,gueris,depistes,source_nom,source_url,source_archive,source_type
        # accept:
        #   - granularite=pays + source_type=ministere-sante
        #   - granularite=region + source_type=opencovid19-fr
        # columns: date,maille_code,maille_nom - deces,hospitalises,gueris and cas_confirmes (only availabre for pays)
        df = df[((df.granularite == 'pays') & (df.source_type == 'ministere-sante')) | ((df.granularite == 'region') & (df.source_type == 'opencovid19-fr'))]
        df.drop(columns=[
            'cas_ehpad', 'granularite', 'cas_confirmes_ehpad', 'cas_possibles_ehpad',
            'deces_ehpad', 'reanimation', 'depistes', 'source_nom', 'source_url', 'source_archive', 'source_type'], inplace=True)
        df.rename(columns={
            'maille_code': 'region_code',
            'cas_confirmes': 'cases', 'maille_nom': 'region',
            'hospitalises': 'hospitalized',
            'gueris': 'recovered', 'deces': 'deceased'}, inplace=True)
        df['region'].mask(df.region_code == 'FRA', 'total-france', inplace=True)

    df['date'] = pd.to_datetime(df['date'])
    df.set_index(['date', 'region_code'], inplace=True)
    last_date = df.index.get_level_values('date')[-1]
    dates = df.index.get_level_values(0)

    # column recovered
    if csv_recovered:
        rec_df = pd.read_csv(csv_recovered)
        rec_df.drop(columns=['CCAA'], inplace=True)
        rec_df.rename(columns={
            'fecha': 'date', 'cod_ine': 'region_code',
            'total': 'recovered'}, inplace=True)
        rec_df['date'] = pd.to_datetime(rec_df['date'])
        rec_df.set_index(['date', 'region_code'], inplace=True)
        last_date_rec = rec_df.index.get_level_values('date')[-1]
        if last_date_rec < last_date:
            df = df[dates <= last_date_rec]
            last_date = last_date_rec
            print("[" + datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] Date truncated for " + scope + ". Different dates on files")
        df = df.merge(rec_df, left_index=True, right_index=True, how='left')

    # column deceased
    if csv_deceased:
        dec_df = pd.read_csv(csv_deceased)
        dec_df.drop(columns=['CCAA'], inplace=True)
        dec_df.rename(columns={
            'fecha': 'date', 'cod_ine': 'region_code',
            'total': 'deceased'}, inplace=True)
        dec_df['date'] = pd.to_datetime(dec_df['date'])
        dec_df.set_index(['date', 'region_code'], inplace=True)
        last_date_dec = dec_df.index.get_level_values('date')[-1]
        if last_date_dec < last_date:
            df = df[dates <= last_date_dec]
            last_date = last_date_dec
            print("[" + datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] Date truncated for " + scope + ". Different dates on files")
        df = df.merge(dec_df, left_index=True, right_index=True, how='left')

    # column deceased
    if csv_hospitalized:
        hos_df = pd.read_csv(csv_hospitalized)
        hos_df.drop(columns=['CCAA'], inplace=True)
        hos_df.rename(columns={
            'fecha': 'date', 'cod_ine': 'region_code',
            'total': 'hospitalized'}, inplace=True)
        hos_df['date'] = pd.to_datetime(hos_df['date'])
        hos_df.set_index(['date', 'region_code'], inplace=True)
        last_date_hos = hos_df.index.get_level_values('date')[-1]
        if last_date_hos < last_date:
            df = df[dates <= last_date_hos]
            last_date = last_date_hos
            print("[" + datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] Date truncated for " + scope + ". Different dates on files")
        df = df.merge(hos_df, left_index=True, right_index=True, how='left')

    # column population
    if os.path.isfile(f"{data_directory}/{scope}_population.csv"):
        pop_df = pd.read_csv(f"{data_directory}/{scope}_population.csv")
        if scope == 'world':
            pop_df.set_index('country_name', inplace=True)
            df = df.merge(pop_df, left_on='region',
                          right_index=True, how='left')
        elif scope in ['italy', 'france']:
            pop_df.set_index('region_name', inplace=True)
            df = df.merge(pop_df, left_on='region',
                          right_index=True, how='left')
        else:
            pop_df.set_index('region_code', inplace=True)
            df = df.merge(pop_df, left_index=True,
                          right_index=True, how='left')
    else:
        df['population'] = 0

    df.fillna(0, inplace=True)
    df.sort_index(inplace=True)

    # add total-italy
    if scope == 'italy':
        dates = df.index.get_level_values('date').unique()
        for date in dates:
            date_df = df.loc[date]
            total = date_df.sum()
            total['region'] = 'total-italy'
            df.loc[(date, 0), df.columns] = total.values

    df['cases_per_100k'] = df['cases'] * 100_000 / df['population']
    df['deceased_per_100k'] = df['deceased'] * 100_000 / df['population']
    df['active_cases'] = df['cases'] - df['recovered'] - df['deceased']
    df['active_cases_per_100k'] = df['active_cases'] * 100_000 / df['population']
    if 'hospitalized' in df.columns:
        df['hosp_per_100k'] = df['hospitalized'] * 100_000 / df['population']
        df['increase_hosp'] = 0.0
        df['rolling_hosp'] = 0.0
        df['rolling_hosp_per_100k'] = 0.0

    df['increase_cases'] = 0.0
    df['rolling_cases'] = 0.0
    df['rolling_cases_per_100k'] = 0.0
    df['increase_deceased'] = 0.0
    df['rolling_deceased'] = 0.0
    df['rolling_deceased_per_100k'] = 0.0

    for region in df['region'].unique():
        reg_df = df[df.region == region]
        # cases
        increase = reg_df['cases'] - reg_df['cases'].shift(1)
        rolling = increase.rolling(window=3).mean()
        df['increase_cases'].mask(df.region == region, increase, inplace=True)
        df['rolling_cases'].mask(df.region == region, rolling, inplace=True)
        df['rolling_cases_per_100k'] = df['rolling_cases'] * 100_000 / df['population']
        # deceased
        increase = reg_df['deceased'] - reg_df['deceased'].shift(1)
        rolling = increase.rolling(window=3).mean()
        df['increase_deceased'].mask(df.region == region, increase, inplace=True)
        df['rolling_deceased'].mask(df.region == region, rolling, inplace=True)
        df['rolling_deceased_per_100k'] = df['rolling_deceased'] * 100_000 / df['population']
        # hospitalized
        if 'hospitalized' in df.columns:
            increase = reg_df['hospitalized'] - reg_df['hospitalized'].shift(1)
            rolling = increase.rolling(window=3).mean()
            df['increase_hosp'].mask(df.region == region, increase, inplace=True)
            df['rolling_hosp'].mask(df.region == region, rolling, inplace=True)
            df['rolling_hosp_per_100k'] = df['rolling_hosp'] * 100_000 / df['population']

    df.fillna(0, inplace=True)
    df.sort_index(inplace=True)
    df.to_csv(f"{data_directory}/{scope}_covid19gram.csv")


if __name__ == "__main__":
    update_data(force=False)
