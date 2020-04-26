#!/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
from gettext import gettext as _
import gettext
import locale

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as patches
from matplotlib.font_manager import FontProperties
import seaborn as sns
sns.set_context("notebook")
sns.set_style("whitegrid")
matplotlib.use('Agg')


class COVID19Plot(object):

    LANGUAGES = ['ca', 'es', 'en', 'it']
    PLOT_TYPES = [
        'daily_cases',
        'daily_hospitalized',
        'active_recovered_deceased',
        'active',
        'cases',
        'hosp_normalized',
        # 'deceased',
        'recovered',
        'daily_deceased',
        # 'cases_normalized'
    ]

    MULTIREGION_PLOT_TYPES = [
        'cases',
        'cases_logarithmic',
        'cases_normalized',
        'hospitalized',
        'hospitalized_logarithmic',
        'hospitalized_normalized',
        'deceased_normalized',
    ]

    SCOPE_PLOT_TYPES = [
        'cases',
        'hospitalized',
        'cases_normalized',
        'hosp_normalized',
        'daily_cases_normalized',
        'deceased_normalized',
        'daily_deceased_normalized',
    ]

    BUTTON_PLOT_TYPES = [
        'daily_cases',
        'active_recovered_deceased',
        'cases',
        'recovered',
        'daily_deceased',
    ]

    BUTTON_SCOPE_PLOT_TYPES = [
        'cases',
        'cases_normalized',
        'daily_cases_normalized',
        'deceased_normalized',
        'daily_deceased_normalized',
    ]

    SCOPES = [
        'spain',
        'italy',
        'france',
        'world'
    ]

    AGES = [
        'spain'
    ]

    CB_color_cycle = [
        '#377eb8', '#ff7f00', '#4daf4a',
        '#f781bf', '#a65628', '#984ea3',
        '#999999', '#e41a1c', '#dede00'
    ]

    _source_path = None
    _images_dir = None
    _footer_font = None
    # 'world' and 'spain'
    # each item will contain the dataframe (df), timestamp (ts)
    _sources = {}
    _translations = {}

    def __init__(self, data_directory='data', images_dir='images/'):
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        self._source_path = data_directory
        self._load_translations()
        for scope in self.SCOPES:
            self._reload_data(scope)
        self._images_dir = images_dir
        self._footer_font = FontProperties()
        self._footer_font.set_family('serif')
        self._footer_font.set_style('italic')

    def _reload_data(self, scope):
        csv_path = f"{self._source_path}/{scope}_covid19gram.csv"
        if not os.path.isfile(csv_path):
            raise RuntimeError(f"Datasource {scope} not found ({csv_path})")

        df = pd.read_csv(csv_path)
        # convert date to datetime and set index
        df['date'] = pd.to_datetime(df['date'])
        df.set_index(['date', 'region_code'], inplace=True)
        df.sort_index()
        source = self._sources.get(scope, {})
        source['df'] = df
        source['ts'] = int(os.path.getmtime(csv_path))
        if scope in self.AGES:
            csv_path = f"{self._source_path}/{scope}_ages.csv"
            if not os.path.isfile(csv_path):
                raise RuntimeError(f"Datasource {scope}(Ages) not found ({csv_path})")
            df_ages = pd.read_csv(csv_path)
            df_ages['date'] = pd.to_datetime(df_ages['fecha'])
            df_ages.set_index(['date'], inplace=True)
            df_ages.sort_index(ascending=True)
            source['df_ages'] = df_ages
            # source['ts_ages'] = int(os.path.getmtime(csv_path))
        self._sources[scope] = source

    def _check_new_data(self, scope):
        csv_path = f"{self._source_path}/{scope}_covid19gram.csv"
        if not os.path.isfile(csv_path):
            raise RuntimeError(f"Datasource {scope} not found ({csv_path})")

        source = self._sources.get(scope, {})
        if int(os.path.getmtime(csv_path)) != source.get('ts'):
            self._reload_data(scope)

    def _load_translations(self):
        for language in self.LANGUAGES:
            translation = gettext.translation('messages', localedir='locales', languages=[language])
            translation.install()
            self._translations[language] = translation

    def get_regions(self, scope):
        source = self._sources.get(scope, {})
        df = source.get('df')
        return list(df.region.unique())

    def get_ages(self, scope):
        t = None
        if scope in self.AGES:
            source = self._sources.get(scope, {})
            df = source.get('df_ages')
            last_date = df.index.get_level_values('date')[-1]
            today_df = df.loc[last_date]
            t = today_df['rango_edad'].unique().tolist()
            t.remove('Total')
            t.sort()
        return t

    def get_region_scope(self, region):
        region_scope = None
        for scope in self.SCOPES:
            if region in self.get_regions(scope):
                region_scope = scope
                break
        return region_scope

    def get_summary(self, region, language='en'):
        region_scope = self.get_region_scope(region)
        if not region_scope:
            raise RuntimeError(_('Region not found in any scope'))

        # check if data source has been modified, and reload it if necessary
        self._check_new_data(region_scope)
        source = self._sources.get(region_scope)

        # get region data
        region_df = self._get_plot_data('summary', source.get('df'), region)
        caption = self._get_caption('summary', region_scope, region, language, region_df)
        return caption

    def get_plot_caption(self, plot_type, region, language='en'):
        if plot_type not in self.PLOT_TYPES:
            raise RuntimeError(_('Plot type is not recognized'))

        region_scope = self.get_region_scope(region)
        if not region_scope:
            raise RuntimeError(_('Region not found in any scope'))

        # check if data source has been modified, and reload it if necessary
        self._check_new_data(region_scope)
        source = self._sources.get(region_scope)

        # get region data
        region_df = self._get_plot_data(plot_type, source.get('df'), region)
        caption = self._get_caption(plot_type, region_scope, region, language, region_df)
        return caption

    def get_scope_plot_caption(self, plot_type, scope, language='en'):
        if plot_type not in self.SCOPE_PLOT_TYPES:
            raise RuntimeError(_('Plot type is not recognized'))

        # check if data source has been modified, and reload it if necessary
        self._check_new_data(scope)
        source = self._sources.get(scope)

        # get region data
        df = source.get('df')
        caption = self._get_scope_caption(plot_type, scope, language, df)
        return caption

    def generate_plot(self, plot_type, region, language='en'):
        if plot_type not in self.PLOT_TYPES:
            raise RuntimeError(_('Plot type is not recognized'))

        region_scope = self.get_region_scope(region)
        if not region_scope:
            raise RuntimeError(_('Region not found in any scope'))

        # check if data source has been modified, and reload it if necessary
        self._check_new_data(region_scope)
        source = self._sources.get(region_scope)
        # check if image has already been generated
        if plot_type == 'recovered' and region == f"total-{region_scope}" and region_scope in self.AGES:
            image_fpath = f"{self._images_dir}/{language}_{region}_ages_{source.get('ts')}.png"
        else:
            image_fpath = f"{self._images_dir}/{language}_{region}_{plot_type}_{source.get('ts')}.png"
        if os.path.isfile(image_fpath):
            return image_fpath

        # get region data
        region_df = self._get_plot_data(plot_type, source.get('df'), region)
        self._plot(plot_type, region_scope, region, language, region_df, image_fpath)
        return image_fpath

    def generate_multiregion_plot(self, plot_type, regions, language='en'):
        if plot_type not in self.MULTIREGION_PLOT_TYPES:
            raise RuntimeError(_('Plot type is not recognized'))

        if len(regions) == 0:
            raise RuntimeError(_('No regions given to generate a multiregion plot'))

        region_scope = self.get_region_scope(regions[0])
        if not region_scope:
            raise RuntimeError(_('First region not found in any scope'))

        for region in regions[1:]:
            if region not in self.get_regions(region_scope):
                raise RuntimeError(_("Region {region} not found in first region scope ({region_scope})".format(region=region, region_scope=region_scope)))

        # check if data source has been modified, and reload it if necessary
        self._check_new_data(region_scope)
        source = self._sources.get(region_scope)

        # check if image has already been generated
        region = '-'.join([region for region in sorted(regions)])
        image_fpath = f"{self._images_dir}/{language}_{region}_{plot_type}_{source.get('ts')}.png"
        if os.path.isfile(image_fpath):
            return image_fpath

        df = source.get('df')
        self._multiregion_plot(plot_type, region_scope, regions, language, df, image_fpath)
        return image_fpath

    def generate_scope_plot(self, plot_type, scope, language='en'):
        if plot_type not in self.SCOPE_PLOT_TYPES:
            raise RuntimeError(_('Plot type is not recognized'))

        # check if data source has been modified, and reload it if necessary
        self._check_new_data(scope)
        source = self._sources.get(scope)
        # check if image has already been generated
        image_fpath = f"{self._images_dir}/{language}_{scope}_{plot_type}_{source.get('ts')}.png"
        if os.path.isfile(image_fpath):
            return image_fpath

        # get region data
        df = source.get('df')
        self._scope_plot(plot_type, scope, language, df, image_fpath)
        return image_fpath

    def _get_plot_data(self, plot_type, df, region):
        region_df = df[df.region == region]
        return region_df

    def _get_caption(self, plot_type, scope, region, language, df):
        _ = self._translations[language].gettext
        self._set_locale(language)

        last_data = None
        last_date = df.index.get_level_values('date')[-1].strftime("%d/%B/%Y")
        if plot_type == 'daily_cases':
            v = locale.format_string('%.0f', df['cases'][-1], grouping=True)
            last_data = "  - " + _('Cumulative cases') + ": " + v + "\n"
            v = locale.format_string('%.0f', df['increase_cases'][-1], grouping=True)
            last_data = last_data + "  - " + _('Last day increment') + ": " + v + "\n"
            v = locale.format_string('%.1f', df['rolling_cases'][-1], grouping=True)
            last_data = last_data + "  - " + \
                _('Increment rolling avg (3 days)') + ": " + v
        elif plot_type == 'daily_hospitalized':
            v = locale.format_string('%.0f', df['hospitalized'][-1], grouping=True)
            last_data = "  - " + _('Currently hospitalized') + ": " + v + "\n"
            v = locale.format_string('%.0f', df['increase_hosp'][-1], grouping=True)
            last_data = last_data + "  - " + _('Hospitalized evolution on last day') + ": " + v + "\n"
            v = locale.format_string('%.1f', df['rolling_hosp'][-1], grouping=True)
            last_data = last_data + "  - " + \
                _('Increment rolling avg (3 days)') + ": " + v
        elif plot_type == 'daily_deceased':
            v = locale.format_string('%.0f', df['deceased'][-1], grouping=True)
            last_data = "  - " + _('Total deceased') + ": " + v + "\n"
            v = locale.format_string('%.0f', df['increase_deceased'][-1], grouping=True)
            last_data = last_data + "  - " + _('Deaths on last day') + ": " + v + "\n"
            v = locale.format_string('%.1f', df['rolling_deceased'][-1], grouping=True)
            last_data = last_data + "  - " + \
                _('Deaths rolling avg (3 days)') + ": " + v
        elif plot_type == 'active_recovered_deceased':
            if np.max(df['cases'] > 0):
                v = locale.format_string('%.0f', df['cases'][-1], grouping=True)
                last_data = "  - " + _('Total cases') + ": " + v + "\n"
                v = locale.format_string('%.0f', df['active_cases'][-1], grouping=True)
                last_data = last_data + "  - " + _('Currently infected') + ": " + v + "\n"
            else:
                last_data = ""
            if 'hospitalized' in df.columns and region != "france":
                v = locale.format_string('%.0f', df['hospitalized'][-1], grouping=True)
                last_data = last_data + "  - " + _('Currently hospitalized') + ": " + v + "\n"
            v = locale.format_string('%.0f', df['recovered'][-1], grouping=True)
            last_data = last_data + "  - " + _('Recovered') + ": " + v + "\n"
            v = locale.format_string('%.0f', df['deceased'][-1], grouping=True)
            last_data = last_data + "  - " + _('Deceased') + ": " + v
        elif plot_type == 'active':
            last_data = ""
            if np.max(df['cases'] > 0):
                v = locale.format_string('%.0f', df['active_cases'][-1], grouping=True)
                last_data = "  - " + _('Active cases') + ": " + v + "\n"
            else:
                last_data = ""
            if 'hospitalized' in df.columns and region != "france":
                v = locale.format_string('%.0f', df['hospitalized'][-1], grouping=True)
                last_data = last_data + "  - " + _('Currently hospitalized') + ": " + v + "\n"
        elif plot_type == 'cases':
            last_data = ""
            if np.max(df['cases'] > 0):
                v = locale.format_string('%.0f', df['cases'][-1], grouping=True)
                last_data = "  - " + _('Cumulative cases') + ": " + v + "\n"
            else:
                last_data = ""
            if 'hospitalized' in df.columns and region != "france":
                v = locale.format_string('%.0f', df['hospitalized'][-1], grouping=True)
                last_data = last_data + "  - " + _('Currently hospitalized') + ": " + v + "\n"
        elif plot_type == 'recovered':
            if region == f"total-{scope}" and scope in self.AGES:
                ages = self.get_ages(scope)
                ages.append('Total')
                ambos_df = self._get_ages_df(scope, sex='ambos', total=True)
                last_data = ""
                last_date = ambos_df.index.get_level_values('date')[-1].strftime("%d %B %Y")
                for age in ages:
                    edad_df = ambos_df[ambos_df['rango_edad'] == age]
                    E = edad_df['casos_confirmados'][-1]
                    E_t = locale.format_string('%.0f', E, grouping=True)
                    F = edad_df['fallecidos'][-1]
                    F_t = locale.format_string('%.0f', F, grouping=True)
                    L = 100 * F / E
                    L_t = locale.format_string('%.2f', L)
                    letal = _('case-fatality rate')
                    tl_age = age.replace("y", _("y"))
                    if age == 'Total':
                        tl_age = _('Total')
                    last_data = last_data + f"**    {tl_age}**: {E_t} ({F_t})  __{letal}:__ {L_t}%\n"
                last_data = last_data + "\n__" + _("*Data obtained from the analysis of reported cases with available information on age and sex.") + "__\n"
            else:
                v = locale.format_string(
                    '%.0f', df['recovered'][-1], grouping=True)
                last_data = "  - " + _('Recovered') + ": " + v + "\n"
        elif plot_type == 'deceased':
            v = locale.format_string(
                '%.0f', df['deceased'][-1], grouping=True)
            last_data = "  - " + _('Deceased') + ": " + v + "\n"
        elif plot_type == 'cases_normalized':
            v = locale.format_string(
                '%.1f', df['cases_per_100k'][-1], grouping=True)
            last_data = "  - " + \
                _('Cases per 100k inhabitants') + ": " + v + "\n"
        elif plot_type == 'summary':
            v = locale.format_string('%.0f', df['cases'][-1], grouping=True)
            last_data = "  🦠 " + _('Total cases') + ": `" + v
            v = locale.format_string('%+.0f', df['increase_cases'][-1], grouping=True)
            last_data += " (" + v + ")`\n"
            v = locale.format_string(
                '%.1f', df['cases_per_100k'][-1], grouping=True)
            last_data += "    `" + v + "` __" + _('per 100k inhabitants') + "__\n\n"
            v = locale.format_string('%.0f', df['deceased'][-1], grouping=True)
            last_data += "  ❌ " + _('Total deceased') + ": `" + v
            v = locale.format_string('%+.0f', df['increase_deceased'][-1], grouping=True)
            last_data += " (" + v + ")`\n"
            v = locale.format_string(
                '%.1f', df['deceased_per_100k'][-1], grouping=True)
            last_data += "    `" + v + "` __" + _('per 100k inhabitants') + "__\n\n"
            v = locale.format_string(
                '%.0f', df['recovered'][-1], grouping=True)
            last_data += "  ✅ " + _('Recovered') + ": `" + v + "`\n\n"
            v = locale.format_string('%.0f', df['active_cases'][-1], grouping=True)
            last_data += "  😷 " + _('Active') + ": `" + v + "`\n"

        updated = _("Information on last available data") + " (" + last_date + ")"
        return f"{last_data}\n__{updated}__"

    def _plot(self, plot_type, scope, region, language, df, image_path):
        # set translation to current language
        _ = self._translations[language].gettext
        self._set_locale(language)

        fig, ax = plt.subplots(figsize=(12, 6))
        x = df.index.get_level_values('date')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        title = None
        y_label = None

        if plot_type == 'daily_cases':
            title = _('Cases increase at {region}').format(region=_(region))
            y_label = _('Cases')
            plt.bar(x, df['increase_cases'], alpha=0.3, width=0.9, label=_('Daily increment'))
            plt.fill_between(x, 0, df['rolling_cases'], color='red', alpha=0.5, label=_('Increment rolling avg (3 days)'))
            plt.plot(x, df['rolling_cases'], color='red')
            ax.annotate(f"{df['increase_cases'][-1]:0,.0f}", xy=(x[-1], df['increase_cases'][-1]),
                        xytext=(0, 3), textcoords="offset points", ha='center')
        elif plot_type == 'daily_hospitalized':
            title = _('Hospitalization evolution at {region}').format(region=_(region))
            y_label = _('Hospitalizations')
            plt.bar(x, df['increase_hosp'], alpha=0.6, width=0.9, label=_('Daily increment'), color='darkgoldenrod')
            plt.fill_between(x, 0, df['rolling_hosp'], color='olive', alpha=0.5, label=_('Increment rolling avg (3 days)'))
            plt.plot(x, df['rolling_hosp'], color='olive')
            ax.annotate(f"{df['increase_hosp'][-1]:0,.0f}", xy=(x[-1], df['increase_hosp'][-1]),
                        xytext=(0, 3), textcoords="offset points", ha='center')
        elif plot_type == 'daily_deceased':
            title = _('Daily deaths evolution at {region}').format(region=_(region))
            y_label = _('Deaths')
            plt.bar(x, df['increase_deceased'], alpha=0.5, width=0.9, color='red', label=_('Daily deaths'))
            plt.fill_between(x, 0, df['rolling_deceased'], color='red', alpha=0.2, label=_('Deaths rolling avg (3 days)'))
            plt.plot(x, df['rolling_deceased'], color='red')
            ax.annotate(f"{df['increase_deceased'][-1]:0,.0f}", xy=(x[-1], df['increase_deceased'][-1]),
                        xytext=(0, 3), textcoords="offset points", ha='center')
        elif plot_type == 'active_recovered_deceased':
            title = _('Active cases, recovered and deceased at {region}').format(region=_(region))
            y_label = _('Cases')
            alpha = 0.3
            if np.max(df['active_cases']) > 0:
                plt.fill_between(x, 0, df['active_cases'], alpha=alpha, label=_('Currently infected'))
                plt.plot(x, df['active_cases'])
                ax.annotate(f"{df['active_cases'][-1]:0,.0f}", xy=(x[-1], df['active_cases'][-1]),
                            xytext=(0, 3), textcoords="offset points")
            if 'hospitalized' in df.columns:
                if region != f'total-france' and scope == 'france':
                    title = _('Curr. hospitalized, recovered & deceased at {region}').format(region=_(region))
                else:
                    title = _('Active, hospitalized, recovered and deceased at {region}').format(region=_(region))
                plt.fill_between(x, 0, df['hospitalized'], color='y', alpha=alpha, label=_('Currently hospitalized'))
                plt.plot(x, df['hospitalized'], color='y')
                ax.annotate(f"{df['hospitalized'][-1]:0,.0f}", xy=(x[-1], df['hospitalized'][-1]),
                            xytext=(0, 3), textcoords="offset points")
            plt.fill_between(x, 0, df['recovered'], color='g', alpha=alpha, label=_('Recovered'))
            plt.plot(x, df['recovered'], color='g')
            ax.annotate(f"{df['recovered'][-1]:0,.0f}", xy=(x[-1], df['recovered'][-1]),
                        xytext=(0, 3), textcoords="offset points")
            plt.fill_between(x, 0, df['deceased'], color='red', alpha=alpha, label=_('Deceased'))
            plt.plot(x, df['deceased'], color='red')
            ax.annotate(f"{df['deceased'][-1]:0,.0f}", xy=(x[-1], df['deceased'][-1]),
                        xytext=(0, 3), textcoords="offset points")
        elif plot_type == 'active':
            if np.max(df['active_cases']) > 0:
                title = _('Active cases at {region}').format(region=_(region))
                y_label = _('Cases')
                plt.bar(x, df['active_cases'], alpha=0.5, width=1, label=_('Active cases'))
                ax.annotate(f"{df['active_cases'][-1]:0,.0f}", xy=(x[-1], df['active_cases'][-1]),
                            xytext=(0, 3), textcoords="offset points", ha='center')
            elif 'hospitalized' in df.columns and region != "total-france":
                title = _('Active hospitalizations at {region}').format(region=_(region))
                y_label = _('Hospitalizations')
                plt.bar(x, df['hospitalized'], alpha=0.5, width=1, label=_('Currently hospitalized'), color='y')
                ax.annotate(f"{df['hospitalized'][-1]:0,.0f}", xy=(x[-1], df['hospitalized'][-1]),
                            xytext=(0, 3), textcoords="offset points", ha='center')
        elif plot_type == 'cases':
            if np.max(df['cases']) > 0:
                title = _('Cumulative cases at {region}').format(region=_(region))
                y_label = _('Cases')
                plt.bar(x, df['cases'], alpha=0.5, width=1, label=_('Cases'))
                ax.annotate(f"{df['cases'][-1]:0,.0f}", xy=(x[-1], df['cases'][-1]),
                            xytext=(0, 3), textcoords="offset points", ha='center')
            elif 'hospitalized' in df.columns and region != "total-france":
                title = _('Hospitalizations at {region}').format(region=_(region))
                y_label = _('Hospitalizations')
                plt.bar(x, df['hospitalized'], alpha=0.5, width=1, label=_('Currently hospitalized'), color='y')
                ax.annotate(f"{df['hospitalized'][-1]:0,.0f}", xy=(x[-1], df['hospitalized'][-1]),
                            xytext=(0, 3), textcoords="offset points", ha='center')

        elif plot_type == 'recovered':
            if region == f"total-{scope}" and scope in self.AGES:
                plt.close()
                self._ages_plot(scope, language, image_path)
                return
            title = _('Recovered cases at {region}').format(region=_(region))
            y_label = _('Cases')
            plt.bar(x, df['recovered'], alpha=0.5, width=1, color='g', label=_('Recovered cases'))
            ax.annotate(f"{df['recovered'][-1]:0,.0f}", xy=(x[-1], df['recovered'][-1]),
                        xytext=(0, 3), textcoords="offset points", ha='center')
        elif plot_type == 'deceased':
            title = _('Deaths evolution at {region}').format(region=_(region))
            y_label = _('Deaths')
            plt.bar(x, df['deceased'], alpha=0.5, width=1, color='r', label=_('Deceased'))
            ax.annotate(f"{df['deceased'][-1]:0,.0f}", xy=(x[-1], df['deceased'][-1]),
                        xytext=(0, 3), textcoords="offset points", ha='center')
        elif plot_type == 'cases_normalized':
            title = _('Cases per 100k inhabitants at {region}').format(region=_(region))
            y_label = _('Cases')
            plt.bar(x, df['cases_per_100k'], alpha=0.5, width=1, label=_('Cases'))
            ax.annotate(f"{df['cases_per_100k'][-1]:0,.0f}", xy=(x[-1], df['cases_per_100k'][-1]),
                        xytext=(0, 3), textcoords="offset points", ha='center')
        elif plot_type == 'hosp_normalized':
            title = _('Hospitalizations per 100k inhabitants at {region}').format(region=_(region))
            y_label = _('Hospitalizations')
            plt.bar(x, df['hosp_per_100k'], alpha=0.5, width=1, label=_('Hospitalizations'))
            ax.annotate(f"{df['hosp_per_100k'][-1]:0,.0f}", xy=(x[-1], df['hosp_per_100k'][-1]),
                        xytext=(0, 3), textcoords="offset points", ha='center')

        plt.title(title, fontsize=26)
        ax.set_ylabel(y_label, fontsize=15)
        xlim = self._get_plot_xlim(scope, df)
        if xlim:
            ax.set_xlim(xlim)
        ax.figure.autofmt_xdate()
        ax.legend(loc='upper left', fontsize=17)
        self._add_footer(ax, scope, language)
        plt.savefig(image_path)
        plt.close()

    def _multiregion_plot(self, plot_type, scope, regions, language, df, image_path):
        # set translation to current language
        _ = self._translations[language].gettext
        self._set_locale(language)

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        title = None
        y_label = None
        legend = True
        if plot_type == 'cases_normalized':
            title = _('Cases per 100k inhabitants')
            y_label = _('Cases')
            regions.sort(key=lambda region: df[df.region == region]['cases_per_100k'][-1], reverse=True)
            for region, color in zip(regions, self.CB_color_cycle):
                df_region = df[df.region == region]
                x = df_region.index.get_level_values('date')
                region_name = _(region)
                v = locale.format_string('%.2f', df_region['cases_per_100k'][-1], grouping=True)
                label = f"{region_name} ({v})"
                plt.plot(x, df_region['cases_per_100k'], linewidth=2, color=color, label=label)

        elif plot_type == 'hospitalized_normalized':
            title = _('Hospitalizations per 100k inhabitants')
            y_label = _('Hospitalizations')
            regions.sort(key=lambda region: df[df.region == region]['hosp_per_100k'][-1], reverse=True)
            for region, color in zip(regions, self.CB_color_cycle):
                df_region = df[df.region == region]
                x = df_region.index.get_level_values('date')
                region_name = _(region)
                v = locale.format_string('%.2f', df_region['hosp_per_100k'][-1], grouping=True)
                label = f"{region_name} ({v})"
                plt.plot(x, df_region['hosp_per_100k'], linewidth=2, color=color, label=label)

        elif plot_type == 'cases':
            title = _('Cases')
            y_label = _('Cases')
            regions.sort(key=lambda region: df[df.region == region]['cases'][-1], reverse=True)
            for region, color in zip(regions, self.CB_color_cycle):
                df_region = df[df.region == region]
                x = df_region.index.get_level_values('date')
                v = locale.format_string('%.0f', df_region['cases'][-1], grouping=True)
                region_name = _(region)
                label = f"{region_name} ({v})"
                plt.plot(x, df_region['cases'], linewidth=2, color=color, label=label)

        elif plot_type == 'hospitalized':
            title = _('Hospitalizations')
            y_label = _('Hospitalizations')
            regions.sort(key=lambda region: df[df.region == region]['hospitalized'][-1], reverse=True)
            for region, color in zip(regions, self.CB_color_cycle):
                df_region = df[df.region == region]
                x = df_region.index.get_level_values('date')
                v = locale.format_string('%.0f', df_region['hospitalized'][-1], grouping=True)
                region_name = _(region)
                label = f"{region_name} ({v})"
                plt.plot(x, df_region['hospitalized'], linewidth=2, color=color, label=label)

        elif plot_type == 'cases_logarithmic':
            title = _('Cases, Logarithmic Scale')
            y_label = _('Cases')
            regions.sort(key=lambda region: df[df.region == region]['cases'][-1], reverse=True)
            for region, color in zip(regions, self.CB_color_cycle):
                df_region = df[df.region == region]
                x = df_region.index.get_level_values('date')
                v = locale.format_string('%.0f', df_region['cases'][-1], grouping=True)
                region_name = _(region)
                plt.yscale('log')
                label = f"{region_name} ({v})"
                plt.plot(x, df_region['cases'], linewidth=2, color=color, label=label)

        elif plot_type == 'hospitalized_logarithmic':
            title = _('Hospitalizations, Logarithmic Scale')
            y_label = _('Hospitalizations')
            regions.sort(key=lambda region: df[df.region == region]['hospitalized'][-1], reverse=True)
            for region, color in zip(regions, self.CB_color_cycle):
                df_region = df[df.region == region]
                x = df_region.index.get_level_values('date')
                v = locale.format_string('%.0f', df_region['hospitalized'][-1], grouping=True)
                region_name = _(region)
                plt.yscale('log')
                label = f"{region_name} ({v})"
                plt.plot(x, df_region['hospitalized'], linewidth=2, color=color, label=label)

        elif plot_type == 'deceased_normalized':
            title = _('Deceased per 100k inhabitants')
            y_label = _('Deaths')
            regions.sort(key=lambda region: df[df.region == region]['deceased_per_100k'][-1], reverse=True)
            for region, color in zip(regions, self.CB_color_cycle):
                df_region = df[df.region == region]
                x = df_region.index.get_level_values('date')
                region_name = _(region)
                v = locale.format_string('%.2f', df_region['deceased_per_100k'][-1], grouping=True)
                label = f"{region_name} ({v})"
                plt.plot(x, df_region['deceased_per_100k'], linewidth=2, color=color, label=label)
                # ax.annotate(f"{v} ({region_name})",
                #             xy=(x[-1], df_region['deceased_per_100k'][-1]), xytext=(0, 3),
                #             textcoords="offset points")

        plt.title(title, fontsize=26)
        ax.set_ylabel(y_label, fontsize=15)
        xlim = self._get_plot_xlim(scope, df)
        if xlim:
            ax.set_xlim(xlim)
        ax.figure.autofmt_xdate()
        if legend:
            ax.legend(loc='upper left', fontsize=17)
        self._add_footer(ax, scope, language)
        plt.savefig(image_path)
        plt.close()

    def _ages_plot(self, scope, language, image_path):
        _ = self._translations[language].gettext
        self._set_locale(language)
        ages_df = self._get_ages_df(scope)
        last_date = ages_df.index.get_level_values('date')[-1]
        title = _('Cases by age') + f" ({last_date:%d %B %Y})"
        edades = self.get_ages(scope)

        women_deaths = list(ages_df[ages_df.sexo == 'mujeres']['fallecidos'])
        women_cases = list(ages_df[ages_df.sexo == 'mujeres']['casos_confirmados'])
        men_deaths = list(ages_df[ages_df.sexo == 'hombres']['fallecidos'])
        men_cases = list(ages_df[ages_df.sexo == 'hombres']['casos_confirmados'])

        max_value = max([max(women_cases), max(women_cases)])

        matplotlib.rc('axes', facecolor='white')
        matplotlib.rc('figure.subplot', wspace=.25)

        # Make figure background the same colors as axes
        fig = plt.figure(figsize=(12, 6), facecolor='white')

        # ---MEN data ---
        axes_left = plt.subplot(121)
        # Keep only top and right spines
        axes_left.spines['left'].set_color('none')
        axes_left.spines['right'].set_zorder(10)
        axes_left.spines['bottom'].set_color('none')
        axes_left.xaxis.set_ticks_position('top')
        axes_left.yaxis.set_ticks_position('right')
        axes_left.spines['top'].set_position(('data', len(edades)))
        axes_left.spines['top'].set_color('w')

        # Set axes limits
        interval_ticks = (((max_value // 7) // 500) + 1) * 500
        max_graph = (9 * interval_ticks) + 50
        plt.xlim(max_graph, 0)
        plt.ylim(0, len(edades))

        # Set ticks label
        m_xticks = [tck * interval_ticks for tck in range(9)]
        # m_xticks = [0, 2500, 5000, 7500, 10000, 12500, 15000, 17500]
        m_xticks_t = [_('MEN') if xtck == 0 else locale.format_string('%.0f', xtck, grouping=True) for xtck in m_xticks]
        w_xticks = m_xticks
        m_xticks.reverse()
        w_xticks_t = [_('WOMEN') if xtck == _('MEN') else xtck for xtck in m_xticks_t]
        m_xticks_t.reverse()
        plt.xticks(m_xticks, m_xticks_t)
        axes_left.get_xticklabels()[-1].set_weight('bold')
        axes_left.get_xticklines()[-1].set_markeredgewidth(0)
        for label in axes_left.get_xticklabels():
            label.set_fontsize(10)
        plt.yticks([])

        # Plot data
        for i in range(len(men_deaths)):
            H, h = 0.8, 0.55
            # Death
            value = men_cases[i]
            p = patches.Rectangle(
                (0, i + (1 - H) / 2.0), value, H, fill=True, transform=axes_left.transData,
                lw=0, facecolor='blue', alpha=0.4)
            axes_left.add_patch(p)
            # New cases
            value = men_deaths[i]
            p = patches.Rectangle(
                (0, i + (1 - h) / 2.0), value, h, fill=True, transform=axes_left.transData,
                lw=0, facecolor='blue', alpha=0.9)
            axes_left.add_patch(p)

        # Add a grid
        axes_left.grid(True, linestyle='--', which='major', color='grey', alpha=.25)

        # --- WOMEN data ---
        axes_right = plt.subplot(122, sharey=axes_left)
        # Keep only top and left spines
        axes_right.spines['right'].set_color('none')
        axes_right.spines['left'].set_zorder(10)
        axes_right.spines['bottom'].set_color('none')
        axes_right.xaxis.set_ticks_position('top')
        axes_right.yaxis.set_ticks_position('left')
        axes_right.spines['top'].set_position(('data', len(edades)))
        axes_right.spines['top'].set_color('w')

        # Set axes limits
        plt.xlim(0, max_graph)
        plt.ylim(0, len(edades))

        # Set ticks labels
        w_xticks.reverse()
        # m_xticks_t.reverse()
        plt.xticks(w_xticks, w_xticks_t)
        axes_right.get_xticklabels()[0].set_weight('bold')
        for label in axes_right.get_xticklabels():
            label.set_fontsize(10)
        axes_right.get_xticklines()[1].set_markeredgewidth(0)
        plt.yticks([])

        # Plot data
        for i in range(len(women_deaths)):
            H, h = 0.8, 0.55
            # Death
            value = women_cases[i]
            p = patches.Rectangle(
                (0, i + (1 - H) / 2.0), value, H, fill=True, transform=axes_right.transData,
                lw=0, facecolor='red', alpha=0.4)
            axes_right.add_patch(p)
            # New cases
            value = women_deaths[i]
            p = patches.Rectangle(
                (0, i + (1 - h) / 2.0), value, h, fill=True, transform=axes_right.transData,
                lw=0, facecolor='red', alpha=0.9)
            axes_right.add_patch(p)

        # Add a grid
        axes_right.grid(True, linestyle='--', which='major', color='grey', alpha=.25)

        # Y axis labels
        # We want them to be exactly in the middle of the two y spines
        for i in range(len(edades)):
            x1, y1 = axes_left.transData.transform_point((0, i + .5))
            x2, y2 = axes_right.transData.transform_point((0, i + .5))
            x, y = fig.transFigure.inverted().transform_point(((x1 + x2) / 2, y1))
            tl_age = edades[i].replace("y", _("y"))
            plt.text(x, y, tl_age, transform=fig.transFigure, fontsize=15, weight='bold',
                     horizontalalignment='center', verticalalignment='center')

        # Legend
        arrowprops = dict(arrowstyle="-", color='black',
                          connectionstyle="angle,angleA=0,angleB=90,rad=0")
        x = men_cases[-1]
        axes_left.annotate(_('NEW CASES'), xy=(x + 6000, 8.5), xycoords='data',
                           horizontalalignment='right', fontsize=10,
                           xytext=(-40, -3), textcoords='offset points',
                           arrowprops=arrowprops)

        x = men_deaths[-1]
        axes_left.annotate(_('DEATHS'), xy=(.85 * x, 8.5), xycoords='data',
                           horizontalalignment='right', fontsize=10, xytext=(-50, -25), textcoords='offset points',
                           arrowprops=arrowprops)

        x = women_cases[-1]
        axes_right.annotate(_('NEW CASES'), xy=(x + 5000, 8.5), xycoords='data',
                            horizontalalignment='left', fontsize=10, xytext=(+40, -3), textcoords='offset points',
                            arrowprops=arrowprops)

        x = women_deaths[-1]
        axes_right.annotate(_('DEATHS'), xy=(.9 * x, 8.5), xycoords='data',
                            horizontalalignment='left', fontsize=10,
                            xytext=(+50, -25), textcoords='offset points',
                            arrowprops=arrowprops)

        fig.text(0.5, 0.955, title, horizontalalignment='center', color='black', weight='bold', fontsize='20')
        # Done
        self._add_footer(axes_right, scope, language)
        plt.savefig(image_path)
        plt.close()

    def _scope_plot(self, plot_type, scope, language, df, image_path):
        # set translation to current language
        _ = self._translations[language].gettext
        self._set_locale(language)
        title = None
        legend = False
        color = 'b'
        label = _('Cases')
        last_date = df.index.get_level_values('date')[-1]

        if plot_type == 'cases_normalized':
            title = _('Cases per 100k inhabitants') + f" ({last_date:%d/%B/%Y})"
            field = 'cases_per_100k'
            if scope == 'france':
                title = _('Hospitalizations per 100k inhabitants') + f" ({last_date:%d/%B/%Y})"
                field = 'hosp_per_100k'
                color = 'goldenrod'
        elif plot_type == 'cases':
            title = _('Cases') + f" ({last_date:%d/%B/%Y})"
            field = 'cases'
            color = 'dodgerblue'
            if scope == 'france':
                title = _('Currently hospitalized') + f" ({last_date:%d/%B/%Y})"
                field = 'hospitalized'
                color = 'goldenrod'
        elif plot_type == 'hospitalized':
            title = _('Hospitalizations') + f" ({last_date:%d/%B/%Y})"
            field = 'hospitalized'
            color = 'goldenrod'
        elif plot_type == 'deceased_normalized':
            title = _('Deceased per 100k inhabitants') + f" ({last_date:%d/%B/%Y})"
            field = 'deceased_per_100k'
            color = 'r'
        elif plot_type == 'daily_cases_normalized':
            title = _('New cases per 100k inhabitants') + f" ({last_date:%d/%B/%Y})"
            field = 'rolling_cases_per_100k'
            if scope == 'france':
                title = _('New hospitalizations per 100k inhabitants') + f" ({last_date:%d/%B/%Y})"
                field = 'rolling_hosp_per_100k'
                color = 'goldenrod'
            legend = True
            label = _('Increment rolling avg (3 days)')
        elif plot_type == 'daily_deceased_normalized':
            title = _('New deceased per 100k inhabitants') + f" ({last_date:%d/%B/%Y})"
            field = 'rolling_deceased_per_100k'
            legend = True
            color = 'r'
            label = _('Increment rolling avg (3 days)')

        today_df = df.loc[last_date]
        top_df = self._get_scope_df(plot_type, scope, today_df, field)

        fig, ax = plt.subplots(figsize=(12, 8))
        ax.xaxis.grid(True, linestyle='--', which='major', color='grey', alpha=.25)
        plt.barh(y=top_df['region'], width=top_df[field], alpha=0.4, color=color, label=label)
        for region in top_df['region'].unique():
            value = top_df[top_df.region == region][field].values[0]
            fmt = '%.1f'
            if plot_type == 'cases':
                fmt = '%.0f'
            value_f = locale.format_string(fmt, value, grouping=True)
            ax.annotate(value_f, xy=(value, region),
                        xytext=(3, 0),
                        textcoords="offset points", va='center')

        if plot_type != 'cases':
            if scope != 'world' and scope != 'france':
                total_region = f"total-{scope}"
                total_value = today_df[today_df.region == total_region][field].values[0]
                ax.axvline(total_value, color=color, alpha=0.5)
                total_value_f = locale.format_string('%.1f', total_value, grouping=True)
                ax.annotate(_("National average") + ": " + total_value_f, xy=(total_value, 0),
                            xytext=(3, -20),
                            textcoords="offset points", va='center')

            elif scope == 'world':
                ax.annotate(_("Countries with more than 1,000 cases"), xy=(1, 0), xycoords='axes fraction',
                            xytext=(-20, 20), textcoords='offset pixels',
                            horizontalalignment='right',
                            verticalalignment='bottom')

        plt.title(title, fontsize=20)
        if legend:
            ax.legend(loc='center right', fontsize=10)
        self._add_footer(ax, scope, language)
        plt.savefig(image_path)
        plt.close()

    def _get_scope_caption(self, plot_type, scope, language, df):
        _ = self._translations[language].gettext
        self._set_locale(language)

        last_date = df.index.get_level_values('date')[-1]
        title = None
        field = None
        if plot_type == 'cases_normalized':
            title = _('Cases per 100k inhabitants')
            field = 'cases_per_100k'
            if scope == 'france':
                title = _('Hospitalizations per 100k inhabitants')
                field = 'hosp_per_100k'
        elif plot_type == 'cases':
            title = _('Cases')
            field = 'cases'
            if scope == 'france':
                field = 'hospitalized'
        elif plot_type == 'deceased_normalized':
            title = _('Deceased per 100k inhabitants')
            field = 'deceased_per_100k'
        elif plot_type == 'daily_cases_normalized':
            title = _('New cases per 100k inhabitants')
            field = 'rolling_cases_per_100k'
            if scope == 'france':
                title = _('New hospitalizations per 100k inhabitants')
                field = 'rolling_hosp_per_100k'
        elif plot_type == 'daily_deceased_normalized':
            title = _('New deceased per 100k inhabitants')
            field = 'rolling_deceased_per_100k'
        today_df = df.loc[last_date]
        top_df = self._get_scope_df(plot_type, scope, today_df, field, max_records=5)
        top_df = top_df.sort_values(field, ascending=False)

        last_data = ""
        last_date = last_date.strftime("%d/%B/%Y")

        for region in top_df['region'].unique():
            value = top_df[top_df.region == region][field].values[0]
            fmt = '%.1f'
            if plot_type == 'cases':
                fmt = '%.0f'
            value_f = locale.format_string(fmt, value, grouping=True)
            last_data = last_data + " - " + _(region) + ": " + value_f + "\n"
        updated = _("Information on last available data") + " (" + last_date + "):"
        return f"**{title}**\n\n{updated}\n{last_data}"

    def _get_scope_df(self, plot_type, scope, today_df, field, max_records=20):
        total_region = f"total-{scope}"
        top_df = today_df[today_df.region != total_region]
        if scope == 'world':
            top_df = top_df[today_df.cases > 1000]
        top_df = top_df.sort_values(field, ascending=True)
        top_df = top_df.tail(max_records)
        return top_df

    def _get_ages_df(self, scope, sex=None, total=False):
        source = self._sources.get(scope)
        df = source.get('df_ages')
        last_date = df.index.get_level_values('date')[-1]
        today_df = df.loc[last_date]
        if sex:
            today_df = today_df[today_df['sexo'] == sex]
        if not total:
            today_df = today_df[today_df['rango_edad'] != "Total"]
        return today_df

    def _get_plot_xlim(self, scope, df):
        if scope in ['spain', 'italy']:
            return np.datetime64('2020-03-01')

        # if cases have reached at least 1000, show since it reached 100. Else, 5 cases
        max_cases = np.max(df['cases'])
        if max_cases > 1000:
            dates_gt_100 = df[df.cases > 100].index.get_level_values('date')
            return dates_gt_100[0]
        else:
            dates_gt_5 = df[df.cases > 5].index.get_level_values('date')
            if len(dates_gt_5) > 0:
                return dates_gt_5[0]
        return None

    def _add_footer(self, ax, scope, language):
        # set translation to current language
        _ = self._translations[language].gettext

        ds_credits = ""
        if scope == 'spain':
            ds_name = 'Datadista'
            ds_url = "https://github.com/datadista/datasets/"
            ds_credits = _("Data source from {ds_name} (see {ds_url})").format(ds_name=ds_name, ds_url=ds_url)
        elif scope == 'world':
            ds_name = 'JHU CSSE'
            ds_url = "https://github.com/pomber/covid19"
            ds_credits = _("Data source from {ds_name} through Pomber's JSON API (see {ds_url})").format(ds_name=ds_name, ds_url=ds_url)
        elif scope == 'italy':
            ds_name = 'Ministero della Salute (Italia)'
            ds_url = "https://github.com/pcm-dpc/COVID-19"
            ds_credits = _("Data source from {ds_name} (see {ds_url})").format(ds_name=ds_name, ds_url=ds_url)
        elif scope == 'france':
            ds_name = 'OpenCOVID19-fr'
            ds_url = "https://opencovid19.fr/"
            ds_credits = _("Data source from {ds_name} (see {ds_url})").format(ds_name=ds_name, ds_url=ds_url)

        ax.set_xlabel(
            _('Generated by COVID19gram (telegram bot)') + "\n" + ds_credits,
            position=(1., 0.),
            fontproperties=self._footer_font,
            horizontalalignment='right')

    def _set_locale(self, language):
        try:
            if language == 'es':
                locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
                locale.setlocale(locale.LC_NUMERIC, "es_ES.UTF-8")
            elif language == 'ca':
                locale.setlocale(locale.LC_TIME, "ca_ES.UTF-8")
                locale.setlocale(locale.LC_NUMERIC, "es_ES.UTF-8")
            elif language == 'en':
                locale.setlocale(locale.LC_TIME, "en_GB.UTF-8")
                locale.setlocale(locale.LC_NUMERIC, "en_GB.UTF-8")
            elif language == 'it':
                locale.setlocale(locale.LC_TIME, "it_IT.UTF-8")
                locale.setlocale(locale.LC_NUMERIC, "it_IT.UTF-8")
        except locale.Error:
            pass
