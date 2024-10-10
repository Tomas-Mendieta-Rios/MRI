import numpy as np
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pydeck as pdk
import plotly.express as px
import seaborn.objects as so
st.set_page_config(layout="wide")
color_palette = color_list = sns.color_palette("Blues", n_colors=5)
custom_colors = {
    'Purple_0': '#8570A9',
    'Blue_1': '#9ABECE',
    'Grey_all': '#D3D3D3',
    'Green_Jóvenes': '#6ABF69',
    'Yellow_Adultos': '#EADF6E',
    'Orange_TerceraEdad': '#F0A154'
}
data_dictionary = {
    'Fecha de recepción de datos': 'date_recepcion_data',
    'Edad': 'age',
    'Provincia': 'provincia',
    'Seguiste recomendaciones': 'SEGUISTE_RECOMENDACIONES',
    'Percepción de cambio': 'RECOMENDACIONES_AJUSTE',
    'Exposición luz natural': 'FOTICO_luz_natural_8_15_integrada',
    'Exposición luz artificial': 'FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada',
    'Estudios no foticos integrados': 'NOFOTICO_estudios_integrada',
    'Trabajo no fotico integrado': 'NOFOTICO_trabajo_integrada',
    'Otra actividad habitual no fotica': 'NOFOTICO_otra_actividad_habitual_si_no',
    'Cena no fotica integrada': 'NOFOTICO_cena_integrada',
    'Horario de acostarse - Hábiles': 'HAB_Hora_acostar',
    'Horario decidir dormir - Hábiles': 'HAB_Hora_decidir',
    'Minutos dormir - Hábiles': 'HAB_min_dormir',
    'Hora despertar - Hábiles': 'HAB_Soffw',
    'Alarma - Hábiles': 'NOFOTICO_HAB_alarma_si_no',
    'Siesta habitual integrada': 'HAB_siesta_integrada',
    'Calidad de sueño habitual': 'HAB_calidad',
    'Horario de acostarse (libre)': 'LIB_Hora_acostar',
    'Horario decidir dormir (libre)': 'LIB_Hora_decidir',
    'Minutos dormir (libre)': 'LIB_min_dormir',
    'Hora despertar (libre)': 'LIB_Offf',
    'Alarma libre (sí/no)': 'LIB_alarma_si_no',
    'MEQ Pregunta 1': 'MEQ1',
    'MEQ Pregunta 2': 'MEQ2',
    'MEQ Pregunta 3': 'MEQ3',
    'MEQ Pregunta 4': 'MEQ4',
    'MEQ Pregunta 5': 'MEQ5',
    'MEQ Pregunta 6': 'MEQ6',
    'MEQ Pregunta 7': 'MEQ7',
    'MEQ Pregunta 8': 'MEQ8',
    'MEQ Pregunta 9': 'MEQ9',
    'MEQ Pregunta 10': 'MEQ10',
    'MEQ Pregunta 11': 'MEQ11',
    'MEQ Pregunta 12': 'MEQ12',
    'MEQ Pregunta 13': 'MEQ13',
    'MEQ Pregunta 14': 'MEQ14',
    'MEQ Pregunta 15': 'MEQ15',
    'MEQ Pregunta 16': 'MEQ16',
    'MEQ Pregunta 17': 'MEQ17',
    'MEQ Pregunta 18': 'MEQ18',
    'MEQ Pregunta 19': 'MEQ19',
    'Recomendación - Alarma no fotica (sí/no)': 'rec_NOFOTICO_HAB_alarma_si_no',
    'Recomendación - Luz natural (8-15)': 'rec_FOTICO_luz_natural_8_15_integrada',
    'Recomendación - Luz artificial (8-15)': 'rec_FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada',
    'Recomendación - Estudios no foticos integrados': 'rec_NOFOTICO_estudios_integrada',
    'Recomendación - Trabajo no fotico integrado': 'rec_NOFOTICO_trabajo_integrada',
    'Recomendación - Otra actividad habitual no fotica (sí/no)': 'rec_NOFOTICO_otra_actividad_habitual_si_no',
    'Recomendación - Cena no fotica integrada': 'rec_NOFOTICO_cena_integrada',
    'Recomendación - Siesta habitual integrada': 'rec_HAB_siesta_integrada',
    'MEQ Puntaje total': 'MEQ_score_total',
    'MSFsc': 'MSFsc',
    'Desviación estándar de sueño (habitual)': 'HAB_SDw',
    'Desviación de jet lag social': 'SJL',
    'Hora de inicio de sueño no laboral centrada': 'HAB_SOnw_centrado'
}

class DataLoader: 
    def __init__(self):
        self.df_all = pd.DataFrame()
        
    def load_data(self, before_path, after_path, geo_path):
        df_before = pd.read_csv(before_path)
        df_after = pd.read_csv(after_path)
        df_geo = pd.read_csv(geo_path,sep=';')
        self.df_all = pd.concat([df_before, df_after], ignore_index=True)
        self.df_all['date_recepcion_data'] = pd.to_datetime(self.df_all['date_recepcion_data'])
        self.df_all.sort_values(by=['user_id', 'date_recepcion_data'], ascending=[True, True], inplace=True)
        self.df_all.reset_index(drop=True, inplace=True)
        self.df_all['days_diff'] = self.df_all.groupby('user_id')['date_recepcion_data'].diff().dt.days.fillna(0)
        self.df_all = pd.merge(self.df_all, df_geo, how='left', on='provincia')
        
        return self.df_all
    
class StreamLit:
    def __init__(self,df):
        self.df = df
        self.initialize_filters()
    
    def initialize_filters(self):
        if 'datos' not in st.session_state:
            st.session_state['datos'] = True
            
        if 'age_range_slider' not in st.session_state:
            st.session_state['age_range_slider'] = [self.df['age'].min(), self.df['age'].max()]

        if 'selected_gender' not in st.session_state:
            st.session_state['selected_gender'] = 'All'

        if 'df_selected' not in st.session_state:
            st.session_state['df_selected'] = self.df
            
        if 'age_joven_min' not in st.session_state: 
            st.session_state['age_joven_min'] = 18
            
        if 'age_adult_min' not in st.session_state: 
            st.session_state['age_adult_min'] = 30

        if 'age_tercera_edad_min' not in st.session_state: 
            st.session_state['age_tercera_edad_min'] = 60

        if 'recommendations_selectbox' not in st.session_state:
            st.session_state['recommendations_selectbox'] = 'Si'

        if 'antes_despues' not in st.session_state:
            st.session_state['antes_despues'] = 'Antes'

        if 'entradas_usuarios_filter' not in st.session_state:
            st.session_state['entradas_usuarios_filter'] = 'Entradas'

        if 'all_dates_checkbox' not in st.session_state:
            st.session_state['all_dates_checkbox'] = True

        if 'all_ages_checkbox' not in st.session_state:
            st.session_state['all_ages_checkbox'] = True

        if 'all_genders_checkbox' not in st.session_state:
            st.session_state['all_genders_checkbox'] = True

        if 'all_recommendations_checkbox' not in st.session_state:
           st.session_state['all_recommendations_checkbox'] = True
           
        if 'min_days_diff_input' not in st.session_state:
           st.session_state['min_days_diff_input'] = 10
       
        if 'max_days_diff_input' not in st.session_state:
           st.session_state['max_days_diff_input'] = 20

        if 'plot' not in st.session_state:
            st.session_state['plot'] = 'Edad'

   
    def sidebar(self):
        st.sidebar.header('Filter Options')
        
        st.sidebar.selectbox("Entrada Usuarios", options=["Entradas", "Usuarios"], key='entradas_usuarios_filter')
            
        st.sidebar.checkbox("All Dates",  key='all_dates_checkbox')
        if not st.session_state['all_dates_checkbox']:
            st.sidebar.date_input("Start Date", value=self.df['date_recepcion_data'].min(), key='start_date_input')
            st.sidebar.date_input("End Date", value=self.df['date_recepcion_data'].max(), key='end_date_input')

        st.sidebar.checkbox("All Ages", key='all_ages_checkbox')
        if not st.session_state['all_ages_checkbox']:
            st.sidebar.slider("Age Range", min_value=int(self.df['age'].min()),max_value=int(self.df['age'].max()),value=(int(self.df['age'].min()), int(self.df['age'].max())),key='age_range_slider')

        st.sidebar.checkbox("All Genders",  key='all_genders_checkbox')
        if not st.session_state['all_genders_checkbox']:
            st.sidebar.selectbox("Select Gender", options=self.df['genero'].unique().tolist(), key='gender_selectbox')

        st.sidebar.checkbox("All Recommendations", key='all_recommendations_checkbox')
        if not st.session_state['all_recommendations_checkbox']:
            st.sidebar.selectbox("Siguieron recomendaciones", options=['Si', 'No',"Ambas"], key='recommendations_selectbox')
            min_days_diff = int(self.df['days_diff'].min())
            max_days_diff = int(self.df['days_diff'].max())
            st.sidebar.number_input("Min days difference", min_value=0, max_value=1000,  key='min_days_diff_input')
            st.sidebar.number_input("Max days difference", min_value=0, max_value=1000,  key='max_days_diff_input')
            st.sidebar.selectbox("Antes Después", options=["Antes", "Después", "Ambas"], key='ambas_antes_despues')

        st.sidebar.subheader("Define Age Categories")
        st.sidebar.number_input("Min Age for Jóvenes", min_value=0, max_value=100 ,key='age_joven_min')
        st.sidebar.number_input("Min Age for Adultos", min_value=0, max_value=100, key='age_adult_min')
        st.sidebar.number_input("Min Age for Tercera Edad", min_value=0, max_value=100,  key='age_tercera_edad_min')

        st.sidebar.selectbox("Gráficos", list(data_dictionary.keys()), key='plot')
        if 'datos' not in st.session_state:
            st.session_state['datos'] = True
        st.sidebar.checkbox("Mostrar datos", key='datos')
        
class Filters:
    def __init__(self,df):
        self.df_all = df
        
    def entries_users(self):
        self.result = self.result.drop_duplicates(subset='user_id', keep='last')
    
    def dates(self):
        date_min = pd.to_datetime(st.session_state['start_date_input'])
        date_max = pd.to_datetime(st.session_state['end_date_input'])
        self.result = self.result[(self.result['date_recepcion_data'] >= date_min) & (self.result['date_recepcion_data'] <= date_max +  pd.Timedelta(days=1))] 
   
    def ages(self):
        age_min, age_max = st.session_state['age_range_slider']
        self.result =  self.result[(self.result['age'] >= age_min) & (self.result['age'] <= age_max)]   
    
    def genders(self):
        self.result = self.result[self.result['genero'] == st.session_state['gender_selectbox']]
        
    def recomendations(self):
        days_min = st.session_state['min_days_diff_input']
        days_max = st.session_state['max_days_diff_input']
        rec_filter = st.session_state['recommendations_selectbox']
        when_filter = st.session_state['ambas_antes_despues']

        self.result = self.result.sort_values(by=['user_id', 'date_recepcion_data'], ascending=[True, True])
        self.result = self.result.reset_index(drop=True)
        final_indices = []
        for idx in range(1, len(self.result)):
            if self.result.loc[idx - 1, 'user_id'] == self.result.loc[idx, 'user_id']:
                if rec_filter == 'Ambas':
                    if self.result.loc[idx, 'SEGUISTE_RECOMENDACIONES'] in ['si', 'no']:
                        if days_min <= self.result.loc[idx, 'days_diff'] <= days_max:
                            if when_filter == 'Ambas':
                                final_indices.append(idx - 1)
                                final_indices.append(idx)
                            elif when_filter == 'Antes':
                                final_indices.append(idx - 1)
                            elif when_filter == 'Después':
                                final_indices.append(idx)
                elif rec_filter == 'Si' and self.result.loc[idx, 'SEGUISTE_RECOMENDACIONES'] == 'si':
                    if days_min <= self.result.loc[idx, 'days_diff'] <= days_max:
                        if when_filter == 'Ambas':
                            final_indices.append(idx - 1)
                            final_indices.append(idx)
                        elif when_filter == 'Antes':
                            final_indices.append(idx - 1)
                        elif when_filter == 'Después':
                            final_indices.append(idx)
                elif rec_filter == 'No' and self.result.loc[idx, 'SEGUISTE_RECOMENDACIONES'] == 'no':
                    if days_min <= self.result.loc[idx, 'days_diff'] <= days_max:
                        if when_filter == 'Ambas':
                            final_indices.append(idx - 1)
                            final_indices.append(idx)
                        elif when_filter == 'Antes':
                            final_indices.append(idx - 1)
                        elif when_filter == 'Después':
                            final_indices.append(idx)
        self.result = self.result.loc[final_indices].reset_index(drop=True)
        
    def categorize_age(self):
        def age_category(age):
            if age < st.session_state['age_adult_min']:
                return 'Jóvenes'
            elif age < st.session_state['age_tercera_edad_min']:
                return 'Adultos'
            else:
                return 'Tercera Edad'
        self.result['age_category'] = self.result['age'].apply(age_category)

    def choose_filter(self):
        self.result = self.df_all
        if not st.session_state['all_dates_checkbox']:  
            self.dates()
        if not st.session_state['all_ages_checkbox']:  
            self.ages()
        if st.session_state['age_joven_min'] or st.session_state['age_adult_min'] or st.session_state['age_tercera_edad_min'] :  
            self.categorize_age()
        if not st.session_state['all_genders_checkbox']:  
            self.genders()
        if  st.session_state['all_recommendations_checkbox'] == False:  
            self.recomendations()
        if st.session_state['entradas_usuarios_filter'] == 'Usuarios':
            self.entries_users()
        return self.result

class PlotGenerator:
    def __init__(self,df):
        self.df = df
        self.df_Jovenes = self.df.loc[self.df['age_category'] == 'Jóvenes']
        self.df_Adultos = self.df.loc[self.df['age_category'] == 'Adultos']
        self.df_TerceraEdad = self.df.loc[self.df['age_category'] == 'Tercera Edad']
        self.value_counts_df = None
        self.value_counts_df_RangoEtario = None
        self.bins = None
        
    def choose_plot(self):
        if st.session_state['plot'] == 'Fecha de recepción de datos':
            self.temporal()
        elif st.session_state['plot'] == 'Edad':
            self.bins = 20
            self.value_counts_df = 'age_category'
            self.value_counts_df_RangoEtario = 'genero'
            self.pie_plot()
            self.histo_plot()
        elif st.session_state['plot'] == "Provincia":
            self.map()
        elif st.session_state['plot'] == 'Seguiste recomendaciones':
            self.value_counts_df = self.value_counts_df_RangoEtario = 'SEGUISTE_RECOMENDACIONES'
            self.pie_plot()
            self.bar_plot()
        elif st.session_state['plot'] == 'Percepción de cambio': 
            self.value_counts_df = self.value_counts_df_RangoEtario = 'RECOMENDACIONES_AJUSTE'
            self.pie_plot()
            self.bar_plot()
        elif st.session_state['plot'] == 'Exposición luz natural':
            self.value_counts_df = self.value_counts_df_RangoEtario = 'FOTICO_luz_natural_8_15_integrada'
            st.write('Distintas condiciones exposicion luz natural')
            st.write('0: Se expone poco a la luz solar')
            st.write('1: Se expone medio a la luz solar')
            st.write('2: Se expone medio a la luz solar')
            self.pie_plot()
            self.bar_plot()
        elif st.session_state['plot'] == "Exposición luz artificial":
            self.value_counts_df = self.value_counts_df_RangoEtario = 'FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada'
            self.pie_plot()
            self.bar_plot()
        elif st.session_state['plot'] == "Estudios no foticos integrados":
            self.value_counts_df = self.value_counts_df_RangoEtario = 'NOFOTICO_estudios_integrada'
            self.pie_plot()
            self.bar_plot()
        elif st.session_state['plot'] == "Trabajo no fotico integrado":
            self.value_counts_df = self.value_counts_df_RangoEtario = 'NOFOTICO_trabajo_integrada'
            self.pie_plot()
            self.bar_plot()
        elif st.session_state['plot'] == "Otra actividad habitual no fotica":
            self.value_counts_df = self.value_counts_df_RangoEtario = 'NOFOTICO_otra_actividad_habitual_si_no'
            self.pie_plot()
            self.bar_plot()
        elif st.session_state['plot'] == "Cena no fotica integrada":
            self.value_counts_df = self.value_counts_df_RangoEtario = 'NOFOTICO_cena_integrada'
            self.pie_plot()
            self.bar_plot()
        elif st.session_state['plot'] == "Horario de acostarse - Hábiles":
            time = pd.to_datetime(self.df['HAB_Hora_acostar'], format='%H:%M')
            self.df['HAB_Hora_acostar'] = time.dt.hour + time.dt.minute / 60
            self.df_Jovenes = self.df.loc[self.df['age_category'] == 'Jóvenes']
            self.df_Adultos = self.df.loc[self.df['age_category'] == 'Adultos']
            self.df_TerceraEdad = self.df.loc[self.df['age_category'] == 'Tercera Edad']
            self.bins = 24
            self.histo_plot()
        elif st.session_state['plot'] == 'Horario decidir dormir - Hábiles':
            time = pd.to_datetime(self.df['HAB_Hora_decidir'], format='%H:%M')
            self.df['HAB_Hora_decidir'] = time.dt.hour + time.dt.minute / 60
            self.df_Jovenes = self.df.loc[self.df['age_category'] == 'Jóvenes']
            self.df_Adultos = self.df.loc[self.df['age_category'] == 'Adultos']
            self.df_TerceraEdad = self.df.loc[self.df['age_category'] == 'Tercera Edad']
            self.bins = 24
            self.histo_plot()
        elif st.session_state['plot'] == 'Minutos dormir - Hábiles':
            self.bins = 24
            self.histo_plot()
        elif st.session_state['plot'] == 'Hora despertar - Hábiles':
            time = pd.to_datetime(self.df['HAB_Soffw'], format='%H:%M')
            self.df['HAB_Soffw'] = time.dt.hour + time.dt.minute / 60
            self.df_Jovenes = self.df.loc[self.df['age_category'] == 'Jóvenes']
            self.df_Adultos = self.df.loc[self.df['age_category'] == 'Adultos']
            self.df_TerceraEdad = self.df.loc[self.df['age_category'] == 'Tercera Edad']
            self.bins = 24
            self.histo_plot()
        elif st.session_state['plot'] == 'Alarma - Hábiles':
            self.value_counts_df = self.value_counts_df_RangoEtario = 'NOFOTICO_HAB_alarma_si_no'
            self.pie_plot()
            self.bar_plot()
            

    def pie_plot(self):    
        col_1, col_2, col_3 = st.columns([1,2,1])
        with col_2:
            fig, ax = plt.subplots(figsize=(8, 6))
            value_counts = self.df[self.value_counts_df].value_counts()
            if st.session_state['plot'] == 'Edad':
                colors = [custom_colors['Yellow_Adultos'],custom_colors['Green_Jóvenes'],custom_colors['Orange_TerceraEdad']]
            else:
                colors = color_palette
            ax.pie(value_counts, labels=value_counts.index, autopct='%1.1f%%', startangle=90, colors=colors)
            ax.set_title('Proporción', fontsize=15)
            st.pyplot(fig)
        col1, col2, col3 = st.columns(3)
        with col1:
            fig, ax = plt.subplots(figsize=(8, 6))
            value_counts = self.df_Jovenes[self.value_counts_df_RangoEtario].value_counts()
            if st.session_state['plot'] == 'Edad':
                colors = [custom_colors['Purple_0'],custom_colors['Blue_1']]
            else:
                colors = color_palette
            ax.pie(value_counts, labels=value_counts.index, autopct='%1.1f%%', startangle=90, colors=colors)
            ax.set_title('Proporción Jóvenes', fontsize=15)
            st.pyplot(fig)
        with col2:
            fig, ax = plt.subplots(figsize=(8, 6))
            value_counts = self.df_Adultos[self.value_counts_df_RangoEtario].value_counts()
            if st.session_state['plot'] == 'Edad':
                colors = [custom_colors['Purple_0'],custom_colors['Blue_1']]
            else:
                colors = color_palette
            ax.pie(value_counts, labels=value_counts.index, autopct='%1.1f%%', startangle=90, colors=colors)
            ax.set_title('Proporción Adultos', fontsize=15)
            st.pyplot(fig)
        with col3:
            fig, ax = plt.subplots(figsize=(8, 6))
            value_counts = self.df_TerceraEdad[self.value_counts_df_RangoEtario].value_counts()
            if st.session_state['plot'] == 'Edad':
                colors = [custom_colors['Purple_0'],custom_colors['Blue_1']]
            else:
                colors = color_palette
            ax.pie(value_counts, labels=value_counts.index, autopct='%1.1f%%', startangle=90, colors=colors)
            ax.set_title('Proporción Tercera Edad', fontsize=15)
            st.pyplot(fig)
            
    def temporal(self):
        palette = sns.color_palette("coolwarm", 3)
        col1, col2 = st.columns(2)
        with col1:
            self.df['date_recepcion_data'] = pd.to_datetime(self.df['date_recepcion_data'], format='%Y-%m-%d %H:%M:%S')
            self.df['month'] = self.df['date_recepcion_data'].dt.to_period('M')
            grouped_data = self.df.groupby('month').size().reset_index(name='count')
            grouped_data['month'] = grouped_data['month'].dt.to_timestamp()
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.lineplot(data=grouped_data, x='month', y='count', color=custom_colors['Grey_all'], ax=ax)
            ax.set_title('Entradas por mes', fontsize=20)
            ax.set_xlabel('', fontsize=15)
            ax.set_ylabel('', fontsize=15)
            plt.xticks(rotation=45)
            st.pyplot(fig)

            self.df_Jovenes['date_recepcion_data'] = pd.to_datetime(self.df_Jovenes['date_recepcion_data'], format='%Y-%m-%d %H:%M:%S')
            self.df_Jovenes['month'] = self.df_Jovenes['date_recepcion_data'].dt.to_period('M')
            grouped_data_jovenes = self.df_Jovenes.groupby('month').size().reset_index(name='count')
            grouped_data_jovenes['month'] = grouped_data_jovenes['month'].dt.to_timestamp()
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.lineplot(data=grouped_data_jovenes, x='month', y='count', color=custom_colors['Green_Jóvenes'], ax=ax)
            ax.set_title('Entradas por mes - Jóvenes', fontsize=20)
            ax.set_xlabel('', fontsize=15)
            ax.set_ylabel('', fontsize=15)
            plt.xticks(rotation=45)
            st.pyplot(fig)
            self.df_Adultos['date_recepcion_data'] = pd.to_datetime(self.df_Adultos['date_recepcion_data'], format='%Y-%m-%d %H:%M:%S')
            self.df_Adultos['month'] = self.df_Adultos['date_recepcion_data'].dt.to_period('M')
            grouped_data_adultos = self.df_Adultos.groupby('month').size().reset_index(name='count')
            grouped_data_adultos['month'] = grouped_data_adultos['month'].dt.to_timestamp()

            fig, ax = plt.subplots(figsize=(8, 6))
            sns.lineplot(data=grouped_data_adultos, x='month', y='count', color=custom_colors['Yellow_Adultos'], ax=ax)
            ax.set_title('Entradas por mes - Adultos', fontsize=20)
            ax.set_xlabel('', fontsize=15)
            ax.set_ylabel('', fontsize=15)
            plt.xticks(rotation=45)
            st.pyplot(fig)
            
            self.df_TerceraEdad['date_recepcion_data'] = pd.to_datetime(self.df_TerceraEdad['date_recepcion_data'], format='%Y-%m-%d %H:%M:%S')
            self.df_TerceraEdad['month'] = self.df_TerceraEdad['date_recepcion_data'].dt.to_period('M')
            grouped_data_tercera = self.df_TerceraEdad.groupby('month').size().reset_index(name='count')
            grouped_data_tercera['month'] = grouped_data_tercera['month'].dt.to_timestamp()
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.lineplot(data=grouped_data_tercera, x='month', y='count', color=custom_colors['Orange_TerceraEdad'], ax=ax)
            ax.set_title('Entradas por mes - Tercera Edad', fontsize=20)
            ax.set_xlabel('', fontsize=15)
            ax.set_ylabel('', fontsize=15)
            plt.xticks(rotation=45)
            st.pyplot(fig)

        with col2:
            # Plot for the entire dataset, by gender
            grouped_data_gender = self.df.groupby(['month', 'genero']).size().reset_index(name='count')
            grouped_data_gender['month'] = grouped_data_gender['month'].dt.to_timestamp()

            fig, ax = plt.subplots(figsize=(8, 6))
            sns.lineplot(data=grouped_data_gender, x='month', y='count', hue='genero', ax=ax, palette=[custom_colors['Purple_0'],custom_colors['Blue_1']])
            ax.set_title('Entradas por mes por género', fontsize=20)
            ax.set_xlabel('', fontsize=15)
            ax.set_ylabel('', fontsize=15)
            plt.xticks(rotation=45)
            st.pyplot(fig)

            # Plot for Jóvenes, by gender
            grouped_data_jovenes_gender = self.df_Jovenes.groupby(['month', 'genero']).size().reset_index(name='count')
            grouped_data_jovenes_gender['month'] = grouped_data_jovenes_gender['month'].dt.to_timestamp()

            fig, ax = plt.subplots(figsize=(8, 6))
            sns.lineplot(data=grouped_data_jovenes_gender, x='month', y='count', hue='genero', ax=ax, palette=[custom_colors['Purple_0'],custom_colors['Blue_1']])
            ax.set_title('Entradas por mes por género - Jóvenes', fontsize=20)
            ax.set_xlabel('', fontsize=15)
            ax.set_ylabel('', fontsize=15)
            plt.xticks(rotation=45)
            st.pyplot(fig)

            # Plot for Adultos, by gender
            grouped_data_adultos_gender = self.df_Adultos.groupby(['month', 'genero']).size().reset_index(name='count')
            grouped_data_adultos_gender['month'] = grouped_data_adultos_gender['month'].dt.to_timestamp()

            fig, ax = plt.subplots(figsize=(8, 6))
            sns.lineplot(data=grouped_data_adultos_gender, x='month', y='count', hue='genero', ax=ax, palette=[custom_colors['Purple_0'],custom_colors['Blue_1']])
            ax.set_title('Entradas por mes por género - Adultos', fontsize=20)
            ax.set_xlabel('', fontsize=15)
            ax.set_ylabel('', fontsize=15)
            plt.xticks(rotation=45)
            st.pyplot(fig)

            # Plot for Tercera Edad, by gender
            grouped_data_tercera_gender = self.df_TerceraEdad.groupby(['month', 'genero']).size().reset_index(name='count')
            grouped_data_tercera_gender['month'] = grouped_data_tercera_gender['month'].dt.to_timestamp()

            fig, ax = plt.subplots(figsize=(8, 6))
            sns.lineplot(data=grouped_data_tercera_gender, x='month', y='count', hue='genero', ax=ax, palette=[custom_colors['Purple_0'],custom_colors['Blue_1']])
            ax.set_title('Entradas por mes por género - T. Edad', fontsize=20)
            ax.set_xlabel('', fontsize=15)
            ax.set_ylabel('', fontsize=15)
            plt.xticks(rotation=45)
            st.pyplot(fig)
 
    def histo_plot(self):
        palette = sns.color_palette("coolwarm", 3)  
        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.histplot(data=self.df, x=data_dictionary[st.session_state['plot']], kde=False, bins=self.bins, ax=ax, color=custom_colors['Grey_all'])
            ax.set_title(st.session_state['plot'], fontsize=20)
            ax.set_xlabel('', fontsize=15)
            ax.set_ylabel('', fontsize=15)
            st.pyplot(fig)
            
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.histplot(data=self.df_Jovenes, x=data_dictionary[st.session_state['plot']], kde=False, bins=self.bins, ax=ax, color=custom_colors['Green_Jóvenes'])
            ax.set_title(f"{st.session_state['plot']} Jóvenes", fontsize=20)
            ax.set_xlabel('', fontsize=15)
            ax.set_ylabel('', fontsize=15)
            st.pyplot(fig)
            
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.histplot(data=self.df_Adultos, x=data_dictionary[st.session_state['plot']], kde=False, bins=self.bins, ax=ax, color=custom_colors['Yellow_Adultos'])
            ax.set_title(f"{st.session_state['plot']} Adultos", fontsize=20)
            ax.set_xlabel('', fontsize=15)
            ax.set_ylabel('', fontsize=15)
            st.pyplot(fig)
            
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.histplot(data=self.df_TerceraEdad, x=data_dictionary[st.session_state['plot']], kde=False, bins=self.bins, ax=ax, color=custom_colors['Orange_TerceraEdad'])
            ax.set_title(f"{st.session_state['plot']} Tercera Edad", fontsize=20)
            ax.set_xlabel('', fontsize=15)
            ax.set_ylabel('', fontsize=15)
            st.pyplot(fig)

        with col2:
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.histplot(data=self.df, x=data_dictionary[st.session_state['plot']], hue='genero', kde=False, bins=self.bins, multiple='dodge', ax=ax,palette = [custom_colors['Purple_0'],custom_colors['Blue_1']])
            ax.set_title(f"{st.session_state['plot']} Género ", fontsize=20)
            ax.set_xlabel('', fontsize=15)
            ax.set_ylabel('', fontsize=15)
            st.pyplot(fig)
            
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.histplot(data=self.df_Jovenes, x=data_dictionary[st.session_state['plot']], hue='genero', kde=False, bins=self.bins, multiple='dodge', ax=ax, palette=[custom_colors['Purple_0'],custom_colors['Blue_1']])
            ax.set_title(f"{st.session_state['plot']} Género - Jóvenes", fontsize=20)
            ax.set_xlabel('', fontsize=15)
            ax.set_ylabel('', fontsize=15)
            st.pyplot(fig)
            
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.histplot(data=self.df_Adultos, x=data_dictionary[st.session_state['plot']], hue='genero', kde=False, bins=self.bins, multiple='dodge', ax=ax, palette=[custom_colors['Purple_0'],custom_colors['Blue_1']])
            ax.set_title(f"{st.session_state['plot']} Género - Adultos", fontsize=20)
            ax.set_xlabel('', fontsize=15)
            ax.set_ylabel('', fontsize=15)
            st.pyplot(fig)
            
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.histplot(data=self.df_TerceraEdad, x=data_dictionary[st.session_state['plot']], hue='genero', kde=False, bins=self.bins, multiple='dodge', ax=ax, palette=[custom_colors['Purple_0'],custom_colors['Blue_1']])
            ax.set_title(f"{st.session_state['plot']} Género - T Edad", fontsize=20)
            ax.set_xlabel('', fontsize=15)
            ax.set_ylabel('', fontsize=15)
            st.pyplot(fig)
         
    def bar_plot(self):
        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.countplot(data=self.df, x=data_dictionary[st.session_state['plot']], ax=ax, color=custom_colors['Grey_all'])
            ax.set_title(f"{st.session_state['plot']}", fontsize=20)
            ax.set_ylabel('', fontsize=15)
            ax.set_xlabel('')
            st.pyplot(fig)
                        
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.countplot(data=self.df_Jovenes, x=data_dictionary[st.session_state['plot']], ax=ax, color=custom_colors['Green_Jóvenes'])
            ax.set_title(f"{st.session_state['plot']} - Jóvenes", fontsize=20)
            ax.set_ylabel('', fontsize=15)
            ax.set_xlabel('')
            st.pyplot(fig)
            
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.countplot(data=self.df_Adultos, x=data_dictionary[st.session_state['plot']], ax=ax, color=custom_colors['Yellow_Adultos'])
            ax.set_title(f"{st.session_state['plot']} - Adultos", fontsize=20)
            ax.set_ylabel('', fontsize=15)
            ax.set_xlabel('')
            st.pyplot(fig)
            
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.countplot(data=self.df_Adultos, x=data_dictionary[st.session_state['plot']], ax=ax, color=custom_colors['Orange_TerceraEdad'])
            ax.set_title(f"{st.session_state['plot']} - Tercera Edad", fontsize=20)
            ax.set_ylabel('', fontsize=15)
            ax.set_xlabel('')
            st.pyplot(fig)   
        with col2:   
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.countplot(data=self.df, x=data_dictionary[st.session_state['plot']], ax=ax, palette=[custom_colors['Purple_0'],custom_colors['Blue_1']], hue='genero')
            ax.set_title(f"{st.session_state['plot']}", fontsize=20)
            ax.set_ylabel('', fontsize=15)
            ax.set_xlabel('')
            st.pyplot(fig)
            
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.countplot(data=self.df_Jovenes, x=data_dictionary[st.session_state['plot']], ax=ax, palette=[custom_colors['Purple_0'],custom_colors['Blue_1']], hue='genero')
            ax.set_title(f"{st.session_state['plot']} - Jóvenes", fontsize=20)
            ax.set_ylabel('', fontsize=15)
            ax.set_xlabel('')
            st.pyplot(fig)
            
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.countplot(data=self.df_Adultos, x=data_dictionary[st.session_state['plot']], ax=ax, palette=[custom_colors['Purple_0'],custom_colors['Blue_1']], hue='genero')
            ax.set_title(f"{st.session_state['plot']} - Adultos", fontsize=20)
            ax.set_ylabel('', fontsize=15)
            ax.set_xlabel('')
            st.pyplot(fig)
            
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.countplot(data=self.df_TerceraEdad, x=data_dictionary[st.session_state['plot']], ax=ax, palette=[custom_colors['Purple_0'],custom_colors['Blue_1']], hue='genero')
            ax.set_title(f"{st.session_state['plot']} - T. Edad", fontsize=20)
            ax.set_ylabel('', fontsize=15)
            ax.set_xlabel('')
            st.pyplot(fig)

    def box_plot(self):
        # Convert `HAB_Hora_acostar` to decimal hours
        hab_acostar_time = pd.to_datetime(self.df['HAB_Hora_acostar'], format='%H:%M')
        self.df['HAB_Hora_acostar_decimal'] = hab_acostar_time.dt.hour + hab_acostar_time.dt.minute / 60

        # Filter out missing values if any
        df_filtered = self.df.dropna(subset=['HAB_Hora_acostar_decimal', data_dictionary[st.session_state['plot']]])

        # Create the plot with the same format as your example
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.boxplot(data=df_filtered, x=data_dictionary[st.session_state['plot']], y='HAB_Hora_acostar_decimal', ax=ax, palette='coolwarm')
        
        # Set plot labels and title using `ax`
        ax.set_title(f"{st.session_state['plot']} - Box Plot of Horario Acostarse", fontsize=20)
        ax.set_xlabel('Grupo', fontsize=15)
        ax.set_ylabel('Horario Acostarse (Horas Decimales)', fontsize=15)
        
        # Display the plot using Streamlit
        st.pyplot(fig)
    
    def map(self): 
            layer = pdk.Layer(
                "HeatmapLayer",
                data=self.df,  # Use your DataFrame with latitude and longitude
                get_position='[Longitude, Latitude]',  # Specify the columns for longitude and latitude
                opacity=0.9,  # Heatmap opacity
                radius_pixels=100,  # Radius of influence in pixels
                intensity=1,  # Intensity of the heatmap
            )

            # Define the view (center of the map)
            view_state = pdk.ViewState(
                latitude=self.df['Latitude'].mean(),  # Center the map by the mean latitude
                longitude=self.df['Longitude'].mean(),  # Center the map by the mean longitude
                zoom=5,  # Zoom level
                pitch=50  # Tilt the map for a 3D effect
            )
            # Add a tooltip to display quantities when hovering
            tooltip = {"html": "<b>Province:</b> {provincia}<br><b>Quantity:</b> {quantity}","style": {"backgroundColor": "steelblue","color": "white"}
            }
            # Create the PyDeck deck object
            deck = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)

            # If using Streamlit, render the PyDeck chart
            st.pydeck_chart(deck)

def main():
    data_loader = DataLoader()
    df_all = data_loader.load_data('Data/allData_MiRelojInterno_24Julio2024.csv', 'Data/allData_MiRelojInterno_27Marzo2023.csv','Data/Geo.csv')
    
    streamlit_app = StreamLit(df_all)
    streamlit_app.sidebar()
    filters = Filters(df_all)
    
    df_filtered = filters.choose_filter()  
    df_filtered = filters.result  

    column_order_df_all = ['date_recepcion_data', 'user_id', 'SEGUISTE_RECOMENDACIONES','days_diff','age', 'genero', 'provincia','localidad', 'Latitude','Longitude' ,'RECOMENDACIONES_AJUSTE', 'date_generacion_recomendacion','FOTICO_luz_natural_8_15_integrada', 'FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada','NOFOTICO_estudios_integrada', 'NOFOTICO_trabajo_integrada', 'NOFOTICO_otra_actividad_habitual_si_no','NOFOTICO_cena_integrada', 'HAB_Hora_acostar', 'HAB_Hora_decidir', 'HAB_min_dormir', 'HAB_Soffw','NOFOTICO_HAB_alarma_si_no', 'HAB_siesta_integrada', 'HAB_calidad', 'LIB_Hora_acostar', 'LIB_Hora_decidir','LIB_min_dormir', 'LIB_Offf', 'LIB_alarma_si_no', 'MEQ1', 'MEQ2', 'MEQ3', 'MEQ4', 'MEQ5', 'MEQ6', 'MEQ7','MEQ8', 'MEQ9', 'MEQ10', 'MEQ11', 'MEQ12', 'MEQ13', 'MEQ14', 'MEQ15', 'MEQ16', 'MEQ17', 'MEQ18', 'MEQ19','rec_NOFOTICO_HAB_alarma_si_no', 'rec_FOTICO_luz_natural_8_15_integrada', 'rec_FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada','rec_NOFOTICO_estudios_integrada', 'rec_NOFOTICO_trabajo_integrada', 'rec_NOFOTICO_otra_actividad_habitual_si_no','rec_NOFOTICO_cena_integrada', 'rec_HAB_siesta_integrada', 'MEQ_score_total', 'MSFsc', 'HAB_SDw', 'SJL', 'HAB_SOnw_centrado']
    column_order = ['date_recepcion_data', 'user_id', 'SEGUISTE_RECOMENDACIONES','days_diff','age','age_category', 'genero', 'provincia','localidad', 'Latitude','Longitude' ,'RECOMENDACIONES_AJUSTE', 'date_generacion_recomendacion','FOTICO_luz_natural_8_15_integrada', 'FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada','NOFOTICO_estudios_integrada', 'NOFOTICO_trabajo_integrada', 'NOFOTICO_otra_actividad_habitual_si_no','NOFOTICO_cena_integrada', 'HAB_Hora_acostar', 'HAB_Hora_decidir', 'HAB_min_dormir', 'HAB_Soffw','NOFOTICO_HAB_alarma_si_no', 'HAB_siesta_integrada', 'HAB_calidad', 'LIB_Hora_acostar', 'LIB_Hora_decidir','LIB_min_dormir', 'LIB_Offf', 'LIB_alarma_si_no', 'MEQ1', 'MEQ2', 'MEQ3', 'MEQ4', 'MEQ5', 'MEQ6', 'MEQ7','MEQ8', 'MEQ9', 'MEQ10', 'MEQ11', 'MEQ12', 'MEQ13', 'MEQ14', 'MEQ15', 'MEQ16', 'MEQ17', 'MEQ18', 'MEQ19','rec_NOFOTICO_HAB_alarma_si_no', 'rec_FOTICO_luz_natural_8_15_integrada', 'rec_FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada','rec_NOFOTICO_estudios_integrada', 'rec_NOFOTICO_trabajo_integrada', 'rec_NOFOTICO_otra_actividad_habitual_si_no','rec_NOFOTICO_cena_integrada', 'rec_HAB_siesta_integrada', 'MEQ_score_total', 'MSFsc', 'HAB_SDw', 'SJL', 'HAB_SOnw_centrado']
    df_filtered = df_filtered[column_order]
    df_filtered = df_filtered.sort_values(by=['user_id', 'date_recepcion_data'], ascending=[True, True])
   
    df_all = df_all[column_order_df_all]
    df_all = df_all.sort_values(by=['user_id', 'date_recepcion_data'], ascending=[True, True])
    
    if st.session_state['datos'] == True:
        st.write('df_all')
        st.write(f'Cantidad de usuarios: {len(df_all)}')  
        st.write(df_all)
        
        st.write('Data filtrada')
        st.write(f'Cantidad de usuarios: {len(df_filtered)}')  
        st.write(df_filtered)

    plot_generator = PlotGenerator(df_filtered)
    plot_generator.choose_plot()

main()


#streamlit run '/Users/tomasmendietarios/Library/Mobile Documents/com~apple~CloudDocs/I.T.B.A/MRI/Main/main.py'




