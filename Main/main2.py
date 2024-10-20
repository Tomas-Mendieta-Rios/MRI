import numpy as np
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pydeck as pdk
import plotly.express as px
import seaborn.objects as so


st.set_page_config(layout="wide")

blue = sns.color_palette("Blues", n_colors=5)

orange = sns.color_palette("Oranges", n_colors=5)

yellow = sns.color_palette("YlOrBr", n_colors=5)

green = sns.color_palette("Greens", n_colors=5)

custom_colors = {
    'Green_Jóvenes': '#6ABF69',
    'Green_Jóvenes_0': '#A3D69B',  
    'Green_Jóvenes_1': '#4C8C3D',  
    'Yellow_Adultos': '#EADF6E',
    'Yellow_Adultos_0': '#F5E7A0',  
    'Yellow_Adultos_1': '#D1C050',  
    'Orange_TerceraEdad': '#F0A154',
    'Orange_TerceraEdad_0': '#F6C79B',  
    'Orange_TerceraEdad_1': '#C77733',  
    'Red_Antes': '#F28B82',  
    'Red_Despues': '#B00020',
    'Blue': '#4F83CC',  
    'Blue_0': '#ADD8E6',  
    'Blue_1': '#1E3A5F'   
}

data_dictionary = {
    'Fecha de recepción de datos': 'date_recepcion_data',
    'Edad': 'age',
    'Edad - Torta':'age',
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
    'Calidad de sueño - Hábiles': 'HAB_calidad',
    'Horario de acostarse - Libres': 'LIB_Hora_acostar',
    'Horario decidir dormir - Libres': 'LIB_Hora_decidir',
    'Minutos dormir - Libres': 'LIB_min_dormir',
    'Hora despertar - Libres': 'LIB_Offf',
    'Alarma - Libres': 'LIB_alarma_si_no',
    'Recomendación - Alarma no fotica (sí/no)': 'rec_NOFOTICO_HAB_alarma_si_no',
    'Recomendación - Luz natural (8-15)': 'rec_FOTICO_luz_natural_8_15_integrada',
    'Recomendación - Luz artificial (8-15)': 'rec_FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada',
    'Recomendación - Estudios no foticos integrados': 'rec_NOFOTICO_estudios_integrada',
    'Recomendación - Trabajo no fotico integrado': 'rec_NOFOTICO_trabajo_integrada',
    'Recomendación - Otra actividad habitual no fotica (sí/no)': 'rec_NOFOTICO_otra_actividad_habitual_si_no',
    'Recomendación - Cena no fotica integrada': 'rec_NOFOTICO_cena_integrada',
    'Recomendación - Siesta habitual integrada': 'rec_HAB_siesta_integrada',
    'MEQ Puntaje total': 'MEQ_score_total_tipo',
    'MSFsc': 'MSFsc',
    'Desviación Estándar De Sueño': 'HAB_SDw',
    'Desviación Jet Lag Social': 'SJL',
    'Hora de inicio de sueño no laboral centrada': 'HAB_SOnw_centrado'
}
age_categories = ['Jóvenes', 'Adultos', 'Tercera Edad']
category_colors = {'Jóvenes': custom_colors['Green_Jóvenes'],'Adultos': custom_colors['Yellow_Adultos'],'Tercera Edad': custom_colors['Orange_TerceraEdad']}
category_colors_gender = {'Jóvenes': [custom_colors['Green_Jóvenes_0'], custom_colors['Green_Jóvenes_1']],'Adultos': [custom_colors['Yellow_Adultos_0'], custom_colors['Yellow_Adultos_1']],'Tercera Edad': [custom_colors['Orange_TerceraEdad_0'], custom_colors['Orange_TerceraEdad_1']]}
class DataLoader: 
    def __init__(self):
        self.df = pd.DataFrame()
        
    def load_data(self, before_path, after_path, geo_path):
        df_before = pd.read_csv(before_path)
        df_after = pd.read_csv(after_path)
        df_geo = pd.read_csv(geo_path,sep=';')
        self.df = pd.concat([df_before, df_after], ignore_index=True)
        self.df['date_recepcion_data'] = pd.to_datetime(self.df['date_recepcion_data'])
        self.df.sort_values(by=['user_id', 'date_recepcion_data'], ascending=[True, True], inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        self.df['days_diff'] = self.df.groupby('user_id')['date_recepcion_data'].diff().dt.days.fillna(0)
        self.df = pd.merge(self.df, df_geo, how='left', on='provincia')
        columns_to_fix = ['rec_NOFOTICO_HAB_alarma_si_no','rec_FOTICO_luz_natural_8_15_integrada','rec_FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada','rec_NOFOTICO_estudios_integrada','rec_NOFOTICO_trabajo_integrada','rec_NOFOTICO_otra_actividad_habitual_si_no','rec_NOFOTICO_cena_integrada','rec_HAB_siesta_integrada']
        self.df[columns_to_fix] = self.df[columns_to_fix].fillna('None').astype(str)
        self.df['MEQ_score_total_tipo'] = self.df['MEQ_score_total'].apply(self.define_chronotype)
        
        time = pd.to_datetime(self.df['HAB_Hora_acostar'], format='%H:%M')
        self.df['HAB_Hora_acostar'] = time.dt.hour + time.dt.minute / 60
        
        time = pd.to_datetime(self.df['HAB_Hora_decidir'], format='%H:%M')
        self.df['HAB_Hora_decidir'] = time.dt.hour + time.dt.minute / 60
        
        time = pd.to_datetime(self.df['HAB_Soffw'], format='%H:%M')
        self.df['HAB_Soffw'] = time.dt.hour + time.dt.minute / 60
        
        time = pd.to_datetime(self.df['LIB_Hora_acostar'], format='%H:%M')
        self.df['LIB_Hora_acostar'] = time.dt.hour + time.dt.minute / 60
        
        time = pd.to_datetime(self.df['LIB_Hora_decidir'], format='%H:%M')
        self.df['LIB_Hora_decidir'] = time.dt.hour + time.dt.minute / 60
        
        time = pd.to_datetime(self.df['LIB_Offf'], format='%H:%M')
        self.df['LIB_Offf'] = time.dt.hour + time.dt.minute / 60

        time = self.df['HAB_SDw']
        self.df['HAB_SDw'] = time / 60
        
        self.df = self.categorize_age(self.df,20,60)
        
        return self.df
    
    def define_chronotype(self, score):
        if 16 <= score <= 30:
            return 'Vespertino Ext'
        elif 31 <= score <= 41:
            return 'Vespertino Mod'
        elif 42 <= score <= 58:
            return 'Intermedio'
        elif 59 <= score <= 69:
            return 'Matutino Mod'
        elif 70 <= score <= 86:
            return 'Matutino Ext'
        else:
            return 'Fuera de Rango'
   
    def categorize_age(self, df, age_adult_min, age_tercera_edad_min):
        def age_category(age):
            if age < age_adult_min:
                return 'Jóvenes'
            elif age < age_tercera_edad_min:
                return 'Adultos'
            else:
                return 'Tercera Edad'
        df['age_category'] = df['age'].apply(age_category)
        return df
    
class StreamLit:
    def __init__(self, df, plot_id):
        self.df = df
        self.plot_id = plot_id
        self.initialize_filters()

    def initialize_filters(self):
        if 'datos_' + self.plot_id not in st.session_state:
            st.session_state['datos_' + self.plot_id] = True

        if 'age_category_selectbox_' + self.plot_id not in st.session_state:
            st.session_state['age_category_selectbox_' + self.plot_id] = 'Todos'

        if 'age_range_slider_' + self.plot_id not in st.session_state:
            st.session_state['age_range_slider_' + self.plot_id] = [self.df['age'].min(), self.df['age'].max()]

        if 'df_selected_' + self.plot_id not in st.session_state:
            st.session_state['df_selected_' + self.plot_id] = self.df

        if 'age_joven_min_' + self.plot_id not in st.session_state:
            st.session_state['age_joven_min_' + self.plot_id] = 18

        if 'age_adult_min_' + self.plot_id not in st.session_state:
            st.session_state['age_adult_min_' + self.plot_id] = 30

        if 'age_tercera_edad_min_' + self.plot_id not in st.session_state:
            st.session_state['age_tercera_edad_min_' + self.plot_id] = 60

        if 'recommendations_selectbox_' + self.plot_id not in st.session_state:
            st.session_state['recommendations_selectbox_' + self.plot_id] = 'Si'

        if 'antes_despues_' + self.plot_id not in st.session_state:
            st.session_state['antes_despues_' + self.plot_id] = 'Antes'

        if 'entradas_usuarios_filter_' + self.plot_id not in st.session_state:
            st.session_state['entradas_usuarios_filter_' + self.plot_id] = 'Entradas'

        if 'all_dates_checkbox_' + self.plot_id not in st.session_state:
            st.session_state['all_dates_checkbox_' + self.plot_id] = True

        if 'all_ages_checkbox_' + self.plot_id not in st.session_state:
            st.session_state['all_ages_checkbox_' + self.plot_id] = True

        if 'all_genders_checkbox_' + self.plot_id not in st.session_state:
            st.session_state['all_genders_checkbox_' + self.plot_id] = True

        if 'all_recommendations_checkbox_' + self.plot_id not in st.session_state:
            st.session_state['all_recommendations_checkbox_' + self.plot_id] = True

        if 'min_days_diff_input_' + self.plot_id not in st.session_state:
            st.session_state['min_days_diff_input_' + self.plot_id] = 10

        if 'max_days_diff_input_' + self.plot_id not in st.session_state:
            st.session_state['max_days_diff_input_' + self.plot_id] = 30

        if 'rango_etario_' + self.plot_id not in st.session_state:
            st.session_state['rango_etario_' + self.plot_id] = True

        if 'define_age_category_' + self.plot_id not in st.session_state:
            st.session_state['define_age_category_' + self.plot_id] = True
        
        if 'entradas_usuarios_checkbox_' + self.plot_id not in st.session_state:
            st.session_state['entradas_usuarios_checkbox_' + self.plot_id] = True
        if 'plot_' + self.plot_id not in st.session_state:
            st.session_state['plot_' + self.plot_id] = 'Edad'
        

    def sidebar(self):
        
        st.sidebar.selectbox('Gráfico', list(data_dictionary.keys()), key='plot_'+ self.plot_id)
     
        st.sidebar.checkbox('Entradas - Usuarios', key='entradas_usuarios_checkbox_' + self.plot_id)
        if not st.session_state['entradas_usuarios_checkbox_' + self.plot_id]:
            st.sidebar.selectbox(f"Entrada Usuarios ", options=["Entradas", "Usuarios"], key='entradas_usuarios_filter_' + self.plot_id)
       
        st.sidebar.checkbox("Recomendaciones", key='all_recommendations_checkbox_' + self.plot_id)
        if not st.session_state['all_recommendations_checkbox_' + self.plot_id]:
            st.sidebar.selectbox("Siguieron recomendaciones", options=['Si', 'No',"Ambas"], key='recommendations_selectbox_'  + self.plot_id)
            min_days_diff = int(self.df['days_diff'].min())
            max_days_diff = int(self.df['days_diff'].max())
            st.sidebar.number_input("Min days difference", min_value=0, max_value=1000, value=10,  key='min_days_diff_input_'  + self.plot_id)
            st.sidebar.number_input("Max days difference", min_value=0, max_value=1000, value = 30,  key='max_days_diff_input_' + self.plot_id)
            st.sidebar.selectbox("Antes Después", options=["Antes", "Después", "Ambas"], key='ambas_antes_despues_' + self.plot_id)

        st.sidebar.checkbox(f'Fechas', key='all_dates_checkbox_' + self.plot_id)
        if not st.session_state['all_dates_checkbox_' + self.plot_id]:
            st.sidebar.date_input(f"Start Date", value=self.df['date_recepcion_data'].min(), key='start_date_input_' + self.plot_id)
            st.sidebar.date_input(f"End Date", value=self.df['date_recepcion_data'].max(), key='end_date_input_' + self.plot_id)

        st.sidebar.checkbox(f"Géneros", key='all_genders_checkbox_' + self.plot_id)
        if not st.session_state['all_genders_checkbox_' + self.plot_id]:
            st.sidebar.selectbox(f"Select Gender", options=self.df['genero'].unique().tolist(), key='selected_gender_' + self.plot_id)
        

        st.sidebar.checkbox(f"Edades", key='all_ages_checkbox_' + self.plot_id)
        if not st.session_state['all_ages_checkbox_' + self.plot_id]:
            st.sidebar.slider(f"Age Range", min_value=int(self.df['age'].min()), max_value=int(self.df['age'].max()), value=(int(self.df['age'].min()), int(self.df['age'].max())), key='age_range_slider_' + self.plot_id)
            st.sidebar.selectbox(f"Seleccionar Rango Etario", ['Todos', 'Jóvenes', 'Adultos', 'Tercera Edad'], key='age_category_selectbox_' + self.plot_id)
        
        st.sidebar.checkbox("Rangos etarios", key='define_age_category_' + self.plot_id )
        if not st.session_state['define_age_category_'+ self.plot_id] :
            st.sidebar.number_input("Min Age for Jóvenes", min_value=0, max_value=100 ,value = 18, key='age_joven_min_'+ self.plot_id)
            st.sidebar.number_input("Min Age for Adultos", min_value=0, max_value=100,value = 30, key='age_adult_min_'+ self.plot_id)
            st.sidebar.number_input("Min Age for Tercera Edad", min_value=0, max_value=100,value = 60,  key='age_tercera_edad_min_'+ self.plot_id)
        
        st.sidebar.checkbox("Mostrar datos", key='datos_' + self.plot_id)

class Filters:
    def __init__(self, df, plot_id):
        self.df = df
        self.result = pd.DataFrame()
        self.plot_id = plot_id

    def entries_users(self, df):
        return df.drop_duplicates(subset='user_id', keep='last')

    def dates(self, df):
        date_min = pd.to_datetime(st.session_state[f'start_date_input_{self.plot_id}'])
        date_max = pd.to_datetime(st.session_state[f'end_date_input_{self.plot_id}'])
        return df[(df['date_recepcion_data'] >= date_min) & (df['date_recepcion_data'] <= date_max + pd.Timedelta(days=1))]

    def ages(self, df):
        age_min, age_max = st.session_state[f'age_range_slider_{self.plot_id}']
        return df[(df['age'] >= age_min) & (df['age'] <= age_max)]

    def genders(self, df, gender):
        return df[df['genero'] == gender ]
    
    def select_age_category(self, df, age_category):
        return df[df['age_category'] == age_category]

    def recomendations(self, df, days_min, days_max, rec_filter, when_filter):
        df = df.sort_values(by=['user_id', 'date_recepcion_data'], ascending=[True, True])
        df = df.reset_index(drop=True)
        final_indices = []
        for idx in range(1, len(df)):
            if df.loc[idx - 1, 'user_id'] == df.loc[idx, 'user_id']:
                if rec_filter == 'Ambas':
                    if df.loc[idx, 'SEGUISTE_RECOMENDACIONES'] in ['si', 'no']:
                        if days_min <= df.loc[idx, 'days_diff'] <= days_max:
                            if when_filter == 'Ambas':
                                final_indices.append(idx - 1)
                                final_indices.append(idx)
                            elif when_filter == 'Antes':
                                final_indices.append(idx - 1)
                            elif when_filter == 'Después':
                                final_indices.append(idx)
                elif rec_filter == 'Si' and df.loc[idx, 'SEGUISTE_RECOMENDACIONES'] == 'si':
                    if days_min <= df.loc[idx, 'days_diff'] <= days_max:
                        if when_filter == 'Ambas':
                            final_indices.append(idx - 1)
                            final_indices.append(idx)
                        elif when_filter == 'Antes':
                            final_indices.append(idx - 1)
                        elif when_filter == 'Después':
                            final_indices.append(idx)
                elif rec_filter == 'No' and df.loc[idx, 'SEGUISTE_RECOMENDACIONES'] == 'no':
                    if days_min <= df.loc[idx, 'days_diff'] <= days_max:
                        if when_filter == 'Ambas':
                            final_indices.append(idx - 1)
                            final_indices.append(idx)
                        elif when_filter == 'Antes':
                            final_indices.append(idx - 1)
                        elif when_filter == 'Después':
                            final_indices.append(idx)
        return df.loc[final_indices].reset_index(drop=True)

    def categorize_age(self, df, age_adult_min, age_tercera_edad_min):
        def age_category(age):
            if age < age_adult_min:
                return 'Jóvenes'
            elif age < age_tercera_edad_min:
                return 'Adultos'
            else:
                return 'Tercera Edad'
        df['age_category'] = df['age'].apply(age_category)
        return df
    
    def choose_filter(self):
        self.result = self.df

        if not st.session_state[f'all_dates_checkbox_{self.plot_id}']:
            self.result = self.dates(self.result)

        if not st.session_state[f'all_ages_checkbox_{self.plot_id}']:
            self.result = self.ages(self.result)

        if  not st.session_state[f'all_genders_checkbox_{self.plot_id}']:
            if not st.session_state[f'selected_gender_{self.plot_id}']:
                genero = 1
            genero = st.session_state[f'selected_gender_{self.plot_id}']
            self.result = self.genders(self.result, genero)
        
        if not st.session_state[f'all_recommendations_checkbox_{self.plot_id}']:
            self.result = self.recomendations(
                self.result,days_min=st.session_state[f'min_days_diff_input_{self.plot_id}'],days_max=st.session_state[f'max_days_diff_input_{self.plot_id}'],rec_filter=st.session_state[f'recommendations_selectbox_{self.plot_id}'],when_filter=st.session_state[f'ambas_antes_despues_{self.plot_id}'])
            
        if not st.session_state['entradas_usuarios_checkbox_' + self.plot_id]:
            if st.session_state[f'entradas_usuarios_filter_{self.plot_id}'] == 'Usuarios':
                self.result = self.entries_users(self.result)

        if not st.session_state[f'rango_etario_{self.plot_id}']:
            self.result = self.select_age_category(self.result)

        if st.session_state[f'age_category_selectbox_{self.plot_id}'] != 'Todos':
            self.result = self.select_age_category(self.result, st.session_state[f'age_category_selectbox_{self.plot_id}'])

        if  st.session_state['define_age_category_' + self.plot_id ] == False:  
            if st.session_state['age_joven_min_' + self.plot_id] or st.session_state['age_adult_min_' + self.plot_id] or st.session_state['age_tercera_edad_min_' + self.plot_id]:  
                self.result = self.categorize_age(self.result,st.session_state['age_joven_min_' + self.plot_id], st.session_state['age_adult_min_' + self.plot_id]  )
class PlotGenerator:
    def __init__(self, df, plot_id):
        self.df = df
        self.plot_id = plot_id
        self.value_counts_df = None
        self.value_counts_df_RangoEtario = None
        self.bins = None

    def choose_plot(self):
        if st.session_state[f'plot_{self.plot_id}'] == 'Fecha de recepción de datos':
            self.temporal()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Edad':
            self.bins = 20
            self.value_counts_df = 'age_category'
            self.value_counts_df_RangoEtario = 'genero'
            self.histo_plot()
            self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Provincia":
            self.map()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Percepción de cambio':
            self.bar_plot()
            self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Exposición luz natural':
            self.bar_plot()
            self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Exposición luz artificial":
            self.bar_plot()
            self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Estudios no foticos integrados":
            self.bar_plot()
            self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Trabajo no fotico integrado":
            self.bar_plot()
            self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Otra actividad habitual no fotica":
            self.bar_plot()
            self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Cena no fotica integrada":
            self.bar_plot()
            self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Horario de acostarse - Hábiles":
            self.bins = 24
            self.histo_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Horario decidir dormir - Hábiles':
            self.bins = 24
            self.histo_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Minutos dormir - Hábiles':
            self.bins = 24
            self.histo_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Hora despertar - Hábiles':
            self.bins = 24
            self.histo_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Alarma - Hábiles':
            self.bar_plot()
            self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Siesta habitual integrada':
            self.bar_plot()
            self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Calidad de sueño - Hábiles':
            self.pie_plot()
            self.bar_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Horario de acostarse - Libre':
            self.bins = 24
            self.histo_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Horario decidir dormir - Libres':
            self.bins = 24
            self.histo_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Minutos dormir - Libres':
            self.bins = 24
            self.histo_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Hora despertar - Libres':
            self.bins = 24
            self.histo_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Alarma - Libres':
            self.bar_plot()
            self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Recomendación - Alarma no fotica (sí/no)":
            self.bar_plot()
            self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Recomendación - Luz natural (8-15)":
            self.bar_plot()
            self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Recomendación - Luz artificial (8-15)":
            self.bar_plot()
            self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Recomendación - Estudios no foticos integrados":
            self.bar_plot()
            self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Recomendación - Trabajo no fotico integrado":
            self.bar_plot()
            self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Recomendación - Otra actividad habitual no fotica (sí/no)":
            self.bar_plot()
            self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Recomendación - Cena no fotica integrada":
            self.bar_plot()
            self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Recomendación - Siesta habitual integrada":
            self.bar_plot()
            self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "MEQ Puntaje total":
            self.bar_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'MSFsc':
            self.bins = 24
            self.histo_plot()
            self.y_edad()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Desviación Estándar De Sueño':
            self.bins = 24
            self.histo_plot()
            self.scatter_plot()
            self.box_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Desviación Jet Lag Social':
            self.scatter_plot()
            self.box_plot()
            self.y_edad()

    def pie_plot(self):    
        fig, ax = plt.subplots(figsize=(8, 6))
        if st.session_state[f'plot_{self.plot_id}'] == 'Edad':
            value_counts = self.df[self.value_counts_df].value_counts()
            colors = [custom_colors['Yellow_Adultos'], custom_colors['Green_Jóvenes'], custom_colors['Orange_TerceraEdad']]
        else:
            value_counts = self.df[data_dictionary[st.session_state[f'plot_{self.plot_id}']]].value_counts()
            colors = blue            
        ax.pie(value_counts, labels=value_counts.index, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.set_title('', fontsize=15)
        st.pyplot(fig)

    def temporal(self):
        self.df['date_recepcion_data'] = pd.to_datetime(self.df['date_recepcion_data'], format='%Y-%m-%d %H:%M:%S')
        self.df['month'] = self.df['date_recepcion_data'].dt.to_period('M')
        grouped_data = self.df.groupby('month').size().reset_index(name='count')
        grouped_data['month'] = grouped_data['month'].dt.to_timestamp()
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.lineplot(data=grouped_data, x='month', y='count', color=custom_colors['Blue'], ax=ax)
        ax.set_title('', fontsize=20)
        ax.set_xlabel('', fontsize=15)
        ax.set_ylabel('', fontsize=15)
        plt.xticks(rotation=45)
        st.pyplot(fig)

    def y_edad(self):
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.lineplot(data=self.df, x='age', y=data_dictionary[st.session_state[f'plot_{self.plot_id}']], color=custom_colors['Blue'], ax=ax, ci=None)
        ax.set_title('', fontsize=20)
        ax.set_xlabel('Edad', fontsize=15)
        ax.set_ylabel(st.session_state[f'plot_{self.plot_id}'], fontsize=15)
        plt.xticks(rotation=45)
        st.pyplot(fig)

    def histo_plot(self): 
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.histplot(data=self.df, x=data_dictionary[st.session_state[f'plot_{self.plot_id}']], kde=False, bins=self.bins, ax=ax, color=custom_colors['Blue'])
        ax.set_title('', fontsize=20)
        ax.set_ylabel('Frecuencia', fontsize=15)
        ax.set_xlabel(st.session_state[f'plot_{self.plot_id}'], fontsize=15)
        st.pyplot(fig)
         
    def bar_plot(self):
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.countplot(data=self.df, x=data_dictionary[st.session_state[f'plot_{self.plot_id}']], ax=ax, color=custom_colors['Blue'])
        ax.set_title('', fontsize=20)
        ax.set_ylabel('Frecuencia', fontsize=15)
        ax.set_xlabel(st.session_state[f'plot_{self.plot_id}'], fontsize=15)
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)

    def scatter_plot(self):
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.scatterplot(data=self.df, x=data_dictionary[st.session_state[f'plot_{self.plot_id}']], y='user_id', ax=ax, color=custom_colors['Red_Antes'])
        ax.set_title('', fontsize=20)
        ax.set_ylabel('', fontsize=15)
        ax.set_xlabel(st.session_state[f'plot_{self.plot_id}'], fontsize=15)
        ax.yaxis.set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)

    def box_plot(self):
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.boxplot(data=self.df, x=data_dictionary[st.session_state[f'plot_{self.plot_id}']], ax=ax, color=custom_colors['Red_Antes'])
        ax.set_title('', fontsize=20)
        ax.set_xlabel(st.session_state[f'plot_{self.plot_id}'], fontsize=15)
        ax.set_ylabel('')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)

    def map(self): 
        layer = pdk.Layer("HeatmapLayer",data=self.df,  get_position='[Longitude, Latitude]',  opacity=0.9,  radius_pixels=100,  intensity=1,  )
        view_state = pdk.ViewState(latitude=self.df['Latitude'].mean(),  longitude=self.df['Longitude'].mean(),  zoom=5,  pitch=50  )
        tooltip = {"html": "<b>Province:</b> {provincia}<br><b>Quantity:</b> {quantity}","style": {"backgroundColor": "steelblue","color": "white"}}
        deck = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)
        st.pydeck_chart(deck)

def main():
    data_loader = DataLoader()
    df_all = data_loader.load_data('Data/allData_MiRelojInterno_24Julio2024.csv', 'Data/allData_MiRelojInterno_27Marzo2023.csv', 'Data/Geo.csv')
    num_plots = st.sidebar.slider("Select the number of plots", min_value=1, max_value=9, value=1, step=1)
    plots_per_row = 3 
    plot_count = 0  
    
    while plot_count < num_plots:
        columns = st.columns(plots_per_row)
        for col in columns:
            if plot_count < num_plots:
                plot_id = f'plot_{plot_count + 1}'  
                st.sidebar.header(f"Plot - {plot_count + 1}")  
                streamlit_app = StreamLit(df_all, plot_id)
                streamlit_app.sidebar()  
                filters = Filters(df_all, plot_id)
                filters.choose_filter()
                df_filtered = filters.result
                column_order = ['date_recepcion_data', 'user_id', 'SEGUISTE_RECOMENDACIONES', 'days_diff', 'age', 'age_category', 'genero', 'provincia', 'localidad', 'Latitude', 'Longitude', 'RECOMENDACIONES_AJUSTE', 'date_generacion_recomendacion', 'FOTICO_luz_natural_8_15_integrada', 'FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada', 'NOFOTICO_estudios_integrada', 'NOFOTICO_trabajo_integrada', 'NOFOTICO_otra_actividad_habitual_si_no', 'NOFOTICO_cena_integrada', 'HAB_Hora_acostar', 'HAB_Hora_decidir', 'HAB_min_dormir', 'HAB_Soffw', 'NOFOTICO_HAB_alarma_si_no', 'HAB_siesta_integrada', 'HAB_calidad', 'LIB_Hora_acostar', 'LIB_Hora_decidir', 'LIB_min_dormir', 'LIB_Offf', 'LIB_alarma_si_no', 'MEQ_score_total', 'MEQ_score_total_tipo', 'MSFsc', 'HAB_SDw', 'SJL', 'HAB_SOnw_centrado']
                df_all = df_all[column_order]
                df_filtered = df_filtered[column_order]

                df_all = df_all.sort_values(by=['user_id', 'date_recepcion_data'], ascending=[True, True])
                df_filtered = df_filtered.sort_values(by=['user_id', 'date_recepcion_data'], ascending=[True, True])
                with col:  
                    if st.session_state['datos_' + plot_id] == False:                    
                        st.write('Datos')
                        st.write(f'Cantidad : {len(df_filtered)}')  
                        st.write(df_filtered)
                    plot_generator = PlotGenerator(df_filtered, plot_id) 
                    plot_generator.choose_plot()  

                plot_count += 1  

if __name__ == "__main__":
    main()

#streamlit run '/Users/tomasmendietarios/Library/Mobile Documents/com~apple~CloudDocs/I.T.B.A/MRI/Main/main2.py'