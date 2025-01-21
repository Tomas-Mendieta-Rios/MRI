import numpy as np
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pydeck as pdk
import plotly.express as px
import seaborn.objects as so
import matplotlib.colors as mcolors  

st.set_page_config(layout="wide")

blue = sns.color_palette("Blues", n_colors=5)
orange = sns.color_palette("Oranges", n_colors=5)
yellow = sns.color_palette("YlOrBr", n_colors=5)
green = sns.color_palette("Greens", n_colors=5)

custom_colors = {
    'Green_Jóvenes': mcolors.rgb2hex(green[2]),   
    'Green_Jóvenes_0': mcolors.rgb2hex(green[1]),  
    'Green_Jóvenes_1': mcolors.rgb2hex(green[3]),  
    'Yellow_Adultos': mcolors.rgb2hex(yellow[1]), 
    'Yellow_Adultos_0': mcolors.rgb2hex(yellow[0]),  
    'Yellow_Adultos_1': mcolors.rgb2hex(yellow[2]),  
    'Orange_TerceraEdad': mcolors.rgb2hex(orange[3]),  
    'Orange_TerceraEdad_0': mcolors.rgb2hex(orange[2]),  
    'Orange_TerceraEdad_1': mcolors.rgb2hex(orange[4]),  
    'Blue': mcolors.rgb2hex(blue[2]),  
    'Blue_0': mcolors.rgb2hex(blue[1]),  
    'Blue_1': mcolors.rgb2hex(blue[3])   
}

def adjust_palette(palette, is_lighter=True):
    if is_lighter:
        return sns.light_palette(palette[1], n_colors=len(palette), reverse=False)
    else:
        return sns.dark_palette(palette[1], n_colors=len(palette), reverse=True)

blue_0 = adjust_palette(blue, is_lighter=True)  # Lighter blue
blue_1 = adjust_palette(blue, is_lighter=False)  # Darker blue

orange_0 = adjust_palette(orange, is_lighter=True)  # Lighter orange
orange_1 = adjust_palette(orange, is_lighter=False)  # Darker orange

yellow_0 = adjust_palette(yellow, is_lighter=True)  # Lighter yellow
yellow_1 = adjust_palette(yellow, is_lighter=False)  # Darker yellow

green_0 = adjust_palette(green, is_lighter=True)    # Lighter green
green_1 = adjust_palette(green, is_lighter=False)  

data_dictionary = {
    'Fecha de recepción de datos': 'date_recepcion_data',
    'Edad': 'age',
    'Provincia': 'provincia',
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
    'Duración Del Sueño - Hábiles': 'HAB_SDw',
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
       
       # columns_to_fix = ['rec_NOFOTICO_HAB_alarma_si_no','rec_FOTICO_luz_natural_8_15_integrada','rec_FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada','rec_NOFOTICO_estudios_integrada','rec_NOFOTICO_trabajo_integrada','rec_NOFOTICO_otra_actividad_habitual_si_no','rec_NOFOTICO_cena_integrada','rec_HAB_siesta_integrada']
       #self.df[columns_to_fix] = self.df[columns_to_fix].fillna('None').astype(str)
        
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
        
        columns_int = [
            'RECOMENDACIONES_AJUSTE',
            'rec_NOFOTICO_HAB_alarma_si_no',
            'rec_FOTICO_luz_natural_8_15_integrada',
            'rec_FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada',
            'rec_NOFOTICO_estudios_integrada',
            'rec_NOFOTICO_otra_actividad_habitual_si_no',
            'rec_NOFOTICO_cena_integrada',
            'rec_HAB_siesta_integrada'
        ]

        self.convert_columns_to_int(columns_int)    
            
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
    
    def convert_columns_to_int(self, columns_to_convert):
        def convert_value(value):
            if pd.isna(value):  # Check for NaN values
                return 'None'  # Return the string 'None' for NaN values
            elif value is None:
                return 'None'  # Return the string 'None' for None values
            elif value == 'None':
                return 'None'  # Return the string 'None' if it is already that
            elif value == 'XX':
                return value  # Keep 'XX' unchanged
            else:
                return int(float(value))  # Convert valid string/float values to int
        for column in columns_to_convert:
            if column != 'RECOMENDACIONES_AJUSTE':
                # Apply conversion to all columns except 'RECOMENDACIONES_AJUSTE'
                self.df[column] = self.df[column].apply(convert_value)
            else:
                # Handle 'RECOMENDACIONES_AJUSTE' specifically
                self.df[column] = self.df[column].apply(lambda value: int(float(value)) if not pd.isna(value) and value != 'None' else value)
                     
class StreamLit:
    def __init__(self, df, plot_id):
        self.df = df
        self.plot_id = plot_id
        self.initialize_filters()

    def initialize_filters(self):
        if 'datos_' + self.plot_id not in st.session_state:
            st.session_state['datos_' + self.plot_id] = True
        
        if 'selected_gender_' + self.plot_id not in st.session_state:
            st.session_state['selected_gender_' + self.plot_id] = 0
       
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

        if 'ambas_antes_despues_' + self.plot_id not in st.session_state:
            st.session_state['ambas_antes_despues_' + self.plot_id] = 'Antes'

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
        
        if 'filtrar_usuarios_checkbox' + self.plot_id  not in st.session_state:
            st.session_state['filtrar_usuarios_checkbox' + self.plot_id ] = True
    
    def sidebar(self):
        st.sidebar.selectbox('Gráfico', list(data_dictionary.keys()), key='plot_'+ self.plot_id)
     
        st.sidebar.checkbox('Entradas - Usuarios', key='entradas_usuarios_checkbox_' + self.plot_id)
        if not st.session_state['entradas_usuarios_checkbox_' + self.plot_id]:
            st.sidebar.selectbox(f"Entrada Usuarios ", options=["Entradas", "Usuarios"], key='entradas_usuarios_filter_' + self.plot_id)
       
        st.sidebar.checkbox("Recomendaciones", key='all_recommendations_checkbox_' + self.plot_id)
        if not st.session_state['all_recommendations_checkbox_' + self.plot_id]:
            
            st.sidebar.selectbox("Siguieron recomendaciones", options=['Si', 'No',"Ambas"], key='recommendations_selectbox_'  + self.plot_id)
            st.sidebar.number_input("Min days difference", min_value=0, max_value=1000, value=10,  key='min_days_diff_input_'  + self.plot_id)
            st.sidebar.number_input("Max days difference", min_value=0, max_value=1000, value = 30,  key='max_days_diff_input_' + self.plot_id)
            st.sidebar.selectbox("Antes Después", options=["Antes", "Después", "Ambas", 'Antes vs Después'  ], key='ambas_antes_despues_' + self.plot_id)

        st.sidebar.checkbox(f'Fechas', key='all_dates_checkbox_' + self.plot_id)
        if not st.session_state['all_dates_checkbox_' + self.plot_id]:
            st.sidebar.date_input(f"Start Date", value=self.df['date_recepcion_data'].min(), key='start_date_input_' + self.plot_id)
            st.sidebar.date_input(f"End Date", value=self.df['date_recepcion_data'].max(), key='end_date_input_' + self.plot_id)

        st.sidebar.checkbox(f"Géneros", key='all_genders_checkbox_' + self.plot_id)
        if not st.session_state['all_genders_checkbox_' + self.plot_id]:
            st.sidebar.selectbox(f"Select Gender", options=self.df['genero'].unique().tolist() , key='selected_gender_' + self.plot_id)
        
        st.sidebar.checkbox(f"Edades", key='all_ages_checkbox_' + self.plot_id)
        if not st.session_state['all_ages_checkbox_' + self.plot_id]:
            st.sidebar.slider(f"Age Range", min_value=int(self.df['age'].min()), max_value=int(self.df['age'].max()), value=(int(self.df['age'].min()), int(self.df['age'].max())), key='age_range_slider_' + self.plot_id)
            st.sidebar.selectbox(f"Seleccionar Rango Etario", ['Todos', 'Jóvenes', 'Adultos', 'Tercera Edad'], key='age_category_selectbox_' + self.plot_id)
        
        st.sidebar.checkbox("Configurar Rangos Etarios", key='define_age_category_' + self.plot_id )
        if not st.session_state['define_age_category_'+ self.plot_id] :
            st.sidebar.number_input("Min Age for Jóvenes", min_value=0, max_value=100 ,value = 18, key='age_joven_min_'+ self.plot_id)
            st.sidebar.number_input("Min Age for Adultos", min_value=0, max_value=100,value = 30, key='age_adult_min_'+ self.plot_id)
            st.sidebar.number_input("Min Age for Tercera Edad", min_value=0, max_value=100,value = 60,  key='age_tercera_edad_min_'+ self.plot_id)
        
        st.sidebar.checkbox("Mostrar datos", key='datos_' + self.plot_id)
        st.sidebar.checkbox("Filtrar por usuarios", key='filtrar_usuarios_checkbox' + self.plot_id )
        if not st.session_state['filtrar_usuarios_checkbox' + self.plot_id]:
            st.sidebar.text_input('Ingrese el ID del usuario', key='filtrar_usuarios_texto'+ self.plot_id)
            st.sidebar.number_input('Ingrese cantidad de entradas', key='filtrar_usuarios_cantidad' + self.plot_id, min_value=1,  step=1, format="%d" )

class Filters:
    def __init__(self, df, plot_id):
        self.df = df
        self.result = pd.DataFrame()
        self.result_antes = pd.DataFrame()
        self.result_despues = pd.DataFrame()
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
        final_indices = set()  # Usamos un conjunto para evitar duplicados
        for idx in range(1, len(df)):
            if df.loc[idx - 1, 'user_id'] == df.loc[idx, 'user_id']:
                if rec_filter == 'Ambas':
                    if df.loc[idx, 'SEGUISTE_RECOMENDACIONES'] in ['si', 'no']:
                        if days_min <= df.loc[idx, 'days_diff'] <= days_max:
                            if when_filter == 'Ambas':
                                final_indices.update([idx - 1, idx])  # Añadimos ambos índices al conjunto
                            elif when_filter == 'Antes':
                                final_indices.add(idx - 1)
                            elif when_filter == 'Después':
                                final_indices.add(idx)
                elif rec_filter == 'Si' and df.loc[idx, 'SEGUISTE_RECOMENDACIONES'] == 'si':
                    if days_min <= df.loc[idx, 'days_diff'] <= days_max:
                        if when_filter == 'Ambas':
                            final_indices.update([idx - 1, idx])
                        elif when_filter == 'Antes':
                            final_indices.add(idx - 1)
                        elif when_filter == 'Después':
                            final_indices.add(idx)
                elif rec_filter == 'No' and df.loc[idx, 'SEGUISTE_RECOMENDACIONES'] == 'no':
                    if days_min <= df.loc[idx, 'days_diff'] <= days_max:
                        if when_filter == 'Ambas':
                            final_indices.update([idx - 1, idx])
                        elif when_filter == 'Antes':
                            final_indices.add(idx - 1)
                        elif when_filter == 'Después':
                            final_indices.add(idx)
        final_indices = sorted(final_indices)
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
    
    def users(self, df, user_id=None):
        if user_id is not None:
            filtered_df = df[df['user_id'] == user_id]
            if filtered_df.empty:
                st.write("El usuario no se encuentra")
            return filtered_df
        return df
    
    def users_count(self, df, n):
        user_counts = df['user_id'].value_counts()
        repeated_users = user_counts[user_counts == n].index
        df = df[df['user_id'].isin(repeated_users)]
        return df

    def choose_filter(self):
        self.result = self.df
        self.result_antes = self.df
        self.result_despues = self.df

        if not st.session_state[f'all_dates_checkbox_{self.plot_id}']:
            self.result = self.dates(self.result)
            self.result_antes = self.dates(self.result_antes)
            self.result_despues = self.dates(self.result_despues)
            
        if not st.session_state[f'all_ages_checkbox_{self.plot_id}']:
            self.result = self.ages(self.result)
            self.result_antes = self.ages(self.result_antes)
            self.result_despues = self.ages(self.result_despues)

        if  not st.session_state[f'all_genders_checkbox_{self.plot_id}']:
            if  st.session_state[f'selected_gender_{self.plot_id}'] != '0 vs 1':
                genero = st.session_state[f'selected_gender_{self.plot_id}']
                self.result = self.genders(self.result, genero)
                self.result_antes = self.genders(self.result_antes, genero)
                self.result_despues = self.genders(self.result_despues, genero)

        if not st.session_state[f'all_recommendations_checkbox_{self.plot_id}']:
            if st.session_state[f'ambas_antes_despues_{self.plot_id}'] != 'Antes vs Después':
                 self.result = self.recomendations(self.result, days_min=st.session_state[f'min_days_diff_input_{self.plot_id}'],days_max=st.session_state[f'max_days_diff_input_{self.plot_id}'], rec_filter=st.session_state[f'recommendations_selectbox_{self.plot_id}'], when_filter=st.session_state[f'ambas_antes_despues_{self.plot_id}'])
            else:
                self.result_antes = self.recomendations(self.result_antes, st.session_state[f'min_days_diff_input_{self.plot_id}'],days_max=st.session_state[f'max_days_diff_input_{self.plot_id}'],rec_filter=st.session_state[f'recommendations_selectbox_{self.plot_id}'], when_filter='Antes')
                self.result_despues = self.recomendations(self.result_despues, st.session_state[f'min_days_diff_input_{self.plot_id}'],days_max=st.session_state[f'max_days_diff_input_{self.plot_id}'],rec_filter=st.session_state[f'recommendations_selectbox_{self.plot_id}'], when_filter='Después')
                

        if not st.session_state[f'rango_etario_{self.plot_id}']:
            self.result = self.select_age_category(self.result)
            self.result_antes = self.select_age_category(self.result_antes)
            self.result_despues = self.select_age_category(self.result_despues)

        if st.session_state[f'age_category_selectbox_{self.plot_id}'] != 'Todos':
            self.result = self.select_age_category(self.result, st.session_state[f'age_category_selectbox_{self.plot_id}'])
            self.result_antes = self.select_age_category(self.result_antes, st.session_state[f'age_category_selectbox_{self.plot_id}'])
            self.result_despues = self.select_age_category(self.result_despues, st.session_state[f'age_category_selectbox_{self.plot_id}'])

        if  st.session_state['define_age_category_' + self.plot_id ] == False:  
            if st.session_state['age_joven_min_' + self.plot_id] or st.session_state['age_adult_min_' + self.plot_id] or st.session_state['age_tercera_edad_min_' + self.plot_id]:  
                self.result = self.categorize_age(self.result,st.session_state['age_joven_min_' + self.plot_id], st.session_state['age_adult_min_' + self.plot_id])
                self.result_antes = self.categorize_age(self.result_antes,st.session_state['age_joven_min_' + self.plot_id], st.session_state['age_adult_min_' + self.plot_id])
                self.result_despues = self.categorize_age(self.result_despues,st.session_state['age_joven_min_' + self.plot_id], st.session_state['age_adult_min_' + self.plot_id])
        
        if  st.session_state['filtrar_usuarios_checkbox' + self.plot_id ] == False: 
            if 'filtrar_usuarios_texto' + self.plot_id in st.session_state and st.session_state['filtrar_usuarios_texto' + self.plot_id]:
                self.result = self.users(self.result, st.session_state['filtrar_usuarios_texto' + self.plot_id])
                self.result_antes = self.users(self.result_antes, st.session_state['filtrar_usuarios_texto' + self.plot_id])
                self.result_despues = self.users(self.result_despues, st.session_state['filtrar_usuarios_texto' + self.plot_id])
            if 'filtrar_usuarios_cantidad' + self.plot_id in st.session_state and st.session_state['filtrar_usuarios_cantidad' + self.plot_id]:
                self.result = self.users_count(self.result, st.session_state['filtrar_usuarios_cantidad' + self.plot_id])
                self.result_antes = self.users_count(self.result_antes, st.session_state['filtrar_usuarios_cantidad' + self.plot_id])
                self.result_despues = self.users_count(self.result_despues, st.session_state['filtrar_usuarios_cantidad' + self.plot_id])
        
        if not st.session_state['entradas_usuarios_checkbox_' + self.plot_id]:
            if st.session_state[f'entradas_usuarios_filter_{self.plot_id}'] == 'Usuarios':
                self.result = self.entries_users(self.result)
                self.result_antes = self.entries_users(self.result_antes)
                self.result_despues = self.entries_users(self.result_despues)
            
class PlotGenerator:
    def __init__(self, df, df_combinado, plot_id):
        self.df = df
        self.plot_id = plot_id
        self.count = None
        self.bins = None
        self.color = custom_colors['Blue']
        self.color_pie = blue
        self.x = None
        self.y = None
        self.x_label = None
        self.y_label = None
        self.rotation = None
        self.rotation2 = None
        self.title = None
        self.y_visible = True
        self.order = None
        self.hue = None
        self.df_combinado = df_combinado
        self.pie = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
        self.fontsize2 = 10
    
    def colors(self):
        age_category = st.session_state['age_category_selectbox_' + self.plot_id]
        gender = st.session_state['selected_gender_' + self.plot_id]

        if st.session_state['all_genders_checkbox_' + self.plot_id] and st.session_state['all_ages_checkbox_' + self.plot_id]:
            self.color_pie = blue
            self.color = custom_colors['Blue']
        
        elif not st.session_state['all_genders_checkbox_' + self.plot_id] and st.session_state['all_ages_checkbox_' + self.plot_id]:
            if gender == 0:
                self.color_pie = blue_0
                self.color = custom_colors['Blue_0']
            elif gender == 1:
                self.color_pie = blue_1
                self.color = custom_colors['Blue_1']

        elif not st.session_state['all_genders_checkbox_' + self.plot_id] and not st.session_state['all_ages_checkbox_' + self.plot_id]:
            
            if age_category == 'Todos':
                if gender == 0:
                    self.color = custom_colors['Blue_0']
                    self.color_pie = blue_0
                elif gender == 1:
                    self.color = custom_colors['Blue_1']
                    self.color_pie = blue_1
            
            elif age_category == 'Jóvenes':
                if gender == 0:
                    self.color = custom_colors['Green_Jóvenes_0']
                    self.color_pie = green_0
                elif gender == 1:
                    self.color = custom_colors['Green_Jóvenes_1']
                    self.color_pie = green_1

            elif age_category == 'Adultos':
                if gender == 0:
                    self.color = custom_colors['Yellow_Adultos_0']
                    self.color_pie = yellow_0
                elif gender == 1:
                    self.color = custom_colors['Yellow_Adultos_1']
                    self.color_pie = yellow_1

            elif age_category == 'Tercera Edad':
                if gender == 0:
                    self.color = custom_colors['Orange_TerceraEdad_0']
                    self.color_pie = orange_0
                elif gender == 1:
                    self.color = custom_colors['Orange_TerceraEdad_1']
                    self.color_pie = orange_1

        elif st.session_state['all_genders_checkbox_' + self.plot_id] and not st.session_state['all_ages_checkbox_' + self.plot_id]:
            if age_category == 'Todos':
                    self.color = custom_colors['Blue']
                    self.color_pie = blue
            elif age_category == 'Jóvenes':
                    self.color = custom_colors['Green_Jóvenes_0']
                    self.color_pie = green
            elif age_category == 'Adultos':
                    self.color = custom_colors['Yellow_Adultos']
                    self.color_pie = yellow
            elif age_category == 'Tercera Edad':
                    self.color = custom_colors['Orange_TerceraEdad']
                    self.color_pie = orange
                    
    def choose_plot(self):
        if st.session_state[f'plot_{self.plot_id}'] == 'Fecha de recepción de datos':
            st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>Fecha de recepción de datos</h1>", unsafe_allow_html=True)
            self.colors()
            self.df['date_recepcion_data'] = pd.to_datetime(self.df['date_recepcion_data'], format='%Y-%m-%d %H:%M:%S')
            self.df['month'] = self.df['date_recepcion_data'].dt.to_period('M')
            grouped_data = self.df.groupby('month').size().reset_index(name='count')
            grouped_data['month'] = grouped_data['month'].dt.to_timestamp()
            self.df = grouped_data
            self.title = 'Uso de la aplicación por mes'
            self.x = 'month'
            self.y = 'count'
            self.lineplot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Edad':
            self.colors()
            self.bins = 20
            self.count = 'age_category'
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.histo_plot()
            self.count = 'age_category'
            self.pie_edad()
        elif st.session_state[f'plot_{self.plot_id}'] == "Provincia":
            self.map()
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.rotation = 45
            self.rotation2 = 80
            self.fontsize2 = 6
            self.count_plot()
            self.rotation = None   
        elif st.session_state[f'plot_{self.plot_id}'] == 'Percepción de cambio':
            st.write('Cuánto crees que cambiaste tus hábitos por las recomendaciones?')
            st.write('1: Muy Poco')
            st.write('5: Completamente')
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.count_plot()
            ##self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Exposición luz natural':
            st.write('Antes de las 15:00 Estás en espacios descubiertos?')
            st.write('0: No')
            st.write('1: Sí, al menos 3 días a la semana')
            st.write('1: Sí, 3 días o más por semana')
            
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.count_plot()
            ##self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Exposición luz artificial":
            st.write('Antes de las 15:00 ¿necesitás encender la luz en el ambiente en el que más estás?')
            st.write('0: sí, casi siempre')
            st.write('1: No, casi nunca')

            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.count_plot()
            ##self.pie_plot()
        
        elif st.session_state[f'plot_{self.plot_id}'] == "Estudios no foticos integrados":
            st.write('Si estás estudiando, ¿tenés clases?')
            st.write('-1: No estudio y/o no tengo clases')
            st.write('0: Sí, menos de 3 días por semana')
            st.write('1: Sí, 3 días o más por semana')
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.count_plot()
            ##self.pie_plot()
        
        elif st.session_state[f'plot_{self.plot_id}'] == "Trabajo no fotico integrado":
            st.write('Estás trabajando?')
            st.write('XX: ??')
            st.write('0: No')
            st.write('-1: Sí, menos de 3 días por semana')
            st.write('1: Sí, 3 días o más por semana')
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.order = ['xx', '-1', '0', '1']
            self.count_plot()
            ##self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Otra actividad habitual no fotica":
            st.write('Hacés alguna otra actividad al menos 3 veces por semana en horarios fijos??')
            st.write('0: No')
            st.write('1: Sí')
        
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.count_plot()
            ##self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Cena no fotica integrada":
            st.write('Cenas habitualmente en el mismo horario?')
            st.write('0: Si')
            st.write('-1: No')
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.count_plot()
            ##self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Horario de acostarse - Hábiles":
            st.write('En días hábiles')
            st.write('Días en que trabajás y/o estudias')
            st.write('¿A qué hora te acostás?')
            st.write('Los diás hábiles me acuesto: HH:MM AM/PM')
            self.bins = 24
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.fontsize2 = 6
            self.histo_plot()
            #self.histo_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Horario decidir dormir - Hábiles':


            st.markdown("<h1 style='color: #D9534F; font-family: Arial, sans-serif;'>En días hábiles (Días en que trabajás y/o estudias)</h1>", unsafe_allow_html=True)

            # Subtítulo en rojo más tenue y un poco más pequeño
            st.markdown("<h3 style='color: #F08080; font-family: Arial, sans-serif;'>¿A qué hora decidís dormirte?</h3>", unsafe_allow_html=True)

            # Último texto en rojo aún más tenue y pequeño
            st.markdown("<p style='color: #FA8072; font-size: 16px; font-family: Arial, sans-serif;'>Una vez que me acosté, decido dormirme: Respuesta en formato HH:MM AM/PM</p>", unsafe_allow_html=True)



            self.bins = 24
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.fontsize2 = 6
            self.histo_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Minutos dormir - Hábiles':
            st.write('En días hábiles')
            st.write('Días en que trabajás y/o estudias')
            st.write('¿Cuántos minutos tardaás en dormirte?')
            st.write('Tardo ... minutos en dormirme: Entero')
            self.bins = 24
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.fontsize2 = 6
            self.histo_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Hora despertar - Hábiles':
            st.write('En días hábiles')
            st.write('Días en que trabajás y/o estudias')
            st.write('¿A qué hora te despertás?')
            st.write('Me despierto: HH:MM AM/PM')
            self.bins = 24
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.fontsize2 = 6
            self.histo_plot()
        
        elif st.session_state[f'plot_{self.plot_id}'] == 'Alarma - Hábiles':
            st.write('En días hábiles')
            st.write('Días en que trabajás y/o estudias')
            st.write('¿Usas alarma o despertador?')
            st.write('0: Si???')
            st.write('1: No??')
            
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.count_plot()
            #self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Siesta habitual integrada':
            st.write('En días hábiles')
            st.write('Días en que trabajás y/o estudias')
            st.write('¿Usas alarma o despertador?')
            st.write('0: Si???')
            st.write('1: No??')
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.count_plot()
           # #self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Calidad de sueño - Hábiles':
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.rotation2 = 45
            self.count_plot()
            ##self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Horario de acostarse - Libres':
            self.colors()
            self.bins = 24
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.fontsize2 = 6
            self.histo_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Horario decidir dormir - Libres':
            self.colors()
            self.bins = 24
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.fontsize2 = 6
            self.histo_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Minutos dormir - Libres':
            self.colors()
            self.bins = 24
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.fontsize2 = 6
            self.histo_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Hora despertar - Libres':
            self.colors()
            self.bins = 24
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.fontsize2 = 6
            self.histo_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Alarma - Libres':
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.count_plot()
            ##self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Recomendación - Alarma no fotica (sí/no)":
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.count_plot()
            ##self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Recomendación - Luz natural (8-15)":
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.count_plot()
            ##self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Recomendación - Luz artificial (8-15)":
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.count_plot()
            ##self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Recomendación - Estudios no foticos integrados":
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.count_plot()
            ##self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Recomendación - Trabajo no fotico integrado":
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.count_plot()
            ##self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Recomendación - Otra actividad habitual no fotica (sí/no)":
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.count_plot()
            ##self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Recomendación - Cena no fotica integrada":
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.count_plot()
            ##self.pie_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == "Recomendación - Siesta habitual integrada":
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.count_plot()
            ##self.pie_plot()

        elif st.session_state[f'plot_{self.plot_id}'] == "MEQ Puntaje total":
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.rotation = 45
            ##self.pie_plot()
            self.fontsize2 = 6
            self.count_plot()
            self.rotation = 45
        elif st.session_state[f'plot_{self.plot_id}'] == 'MSFsc':
            self.colors()
            self.x = 'MEQ_score_total_tipo'
            self.y_label = 'Frecuencia'
            self.rotation = 45
            self.fontsize2 = 6
            self.count_plot()
            data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            ##self.pie_plot()
            self.rotation = None
            self.x ='age'
            self.x_label = 'Edad'
            self.y = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.y_label = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.lineplot()
            self.y = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.y_label = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x = 'NOFOTICO_cena_integrada'
            self.x_label = 'Cena Integrada'
            self.bar_plot()
            
        elif st.session_state[f'plot_{self.plot_id}'] == 'Duración Del Sueño - Hábiles':
            self.bins = 24
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.fontsize2 = 6
            self.histo_plot()
        elif st.session_state[f'plot_{self.plot_id}'] == 'Desviación Jet Lag Social':
            #Scatter Plot
            self.colors()
            self.y = 'user_id'
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = None
            self.y_visible = False
            self.scatter_plot()
            # Box Plot
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_visible = False
            self.y_label = None
            self.y = 'user_id'
            self.box_plot()
            #Line Plot
            self.y = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.y_label = st.session_state[f'plot_{self.plot_id}']
            self.x = 'age'
            self.x_label = 'Edad'
            self.lineplot()
            #Scatter Plot 'Desviación Jet Lag Social' vs MSFsc
            self.y = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.y_visible = True
            self.y_label = st.session_state[f'plot_{self.plot_id}']
            self.x = 'MSFsc'
            self.x_label = 'MSFsc'
            self.scatter_plot()

        elif st.session_state[f'plot_{self.plot_id}'] == 'Hora de inicio de sueño no laboral centrada':
            self.bins=24
            self.colors()
            self.x = data_dictionary[st.session_state[f'plot_{self.plot_id}']]
            self.x_label = st.session_state[f'plot_{self.plot_id}']
            self.y_label = 'Frecuencia'
            self.histo_plot()
            
    def pie_plot(self):    
        fig, ax = plt.subplots(figsize=(8, 6))
        if st.session_state['ambas_antes_despues_' + self.plot_id] != 'Antes vs Después':
            value_counts = self.df[self.pie].value_counts() 
            ax.pie(value_counts, labels=value_counts.index, autopct='%1.1f%%', startangle=90, colors=self.color_pie,labeldistance=1.1, pctdistance=0.5)
            ax.set_title('Distribución General', fontsize=15)
            st.pyplot(fig)
        else:
            col1, col2 = st.columns(2)
            with col1:
                fig,ax= plt.subplots(figsize=(8, 6))
                value_counts_antes = self.df_combinado[self.df_combinado['Periodo'] == 'Antes'][self.pie].value_counts()
                colors_antes = self.color_pie
                ax.pie(value_counts_antes, labels=value_counts_antes.index, autopct='%1.1f%%', startangle=90, colors=colors_antes)
                ax.set_title('Antes', fontsize=15)
                st.pyplot(fig)
            with col2:
                fig,ax= plt.subplots(figsize=(8, 6))
                value_counts_despues = self.df_combinado[self.df_combinado['Periodo'] == 'Después'][self.pie].value_counts()
                colors_despues = self.color_pie
                ax.pie(value_counts_despues, labels=value_counts_despues.index, autopct='%1.1f%%', startangle=90, colors=colors_despues)
                ax.set_title('Después', fontsize=15)
                st.pyplot(fig)

    def pie_edad(self):
        fig, ax = plt.subplots(figsize=(8, 6))
        if not st.session_state['all_genders_checkbox_' + self.plot_id]:
            if st.session_state['selected_gender_' + self.plot_id] == 0:
                colors = [ custom_colors['Yellow_Adultos_0'], custom_colors['Orange_TerceraEdad_0'], custom_colors['Green_Jóvenes_0']]
            elif st.session_state['selected_gender_' + self.plot_id] == 1:
                colors = [ custom_colors['Yellow_Adultos_1'], custom_colors['Orange_TerceraEdad_1'], custom_colors['Green_Jóvenes_1']]
        else:
            colors = [ custom_colors['Yellow_Adultos'], custom_colors['Orange_TerceraEdad'], custom_colors['Green_Jóvenes']]
        value_counts = self.df[self.count].value_counts()
        ax.pie(value_counts, labels=value_counts.index, autopct='%1.1f%%', startangle=90, colors=colors )
        ax.set_title('', fontsize=15)
        st.pyplot(fig)

    def lineplot(self):
        fig, ax = plt.subplots(figsize=(8, 6))
        if st.session_state['ambas_antes_despues_' + self.plot_id] == 'Antes vs Después':
            sns.lineplot(data=self.df_combinado, x=self.x, y=self.y, palette=sns.light_palette(self.color, n_colors=2), ax=ax, hue='Periodo', errorbar=None)
        else:
            sns.lineplot(data=self.df, x=self.x, y=self.y, color=self.color, ax=ax, errorbar=None)
        ax.set_title(self.title, fontsize=20)
        ax.set_xlabel(self.x_label, fontsize=15)
        ax.set_ylabel(self.y_label, fontsize=15)
        plt.xticks(rotation=self.rotation)
        st.pyplot(fig)

    def histo_plot(self): 
        fig, ax = plt.subplots(figsize=(8, 6))
        if st.session_state['ambas_antes_despues_' + self.plot_id] == 'Antes vs Después':
            sns.histplot(data=self.df_combinado, x=self.x, kde=False, bins=self.bins, ax=ax, palette=sns.light_palette(self.color, n_colors=2), hue='Periodo', multiple="dodge") 
        else:
            sns.histplot(data=self.df, x=self.x, kde=False, bins=self.bins, ax=ax, color=self.color)
        for p in ax.patches:
            if p.get_height() > 0:
                ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2, p.get_height() ), ha='center', va='bottom', fontsize=self.fontsize2, color='grey', rotation = self.rotation2)
        ax.set_title(self.title, fontsize=20)
        ax.set_xlabel(self.x_label, fontsize=15)
        ax.set_ylabel(self.y_label, fontsize=15)
        plt.xticks(rotation=self.rotation)
        ax.yaxis.set_visible(self.y_visible)
        st.pyplot(fig)

    def count_plot(self):
            fig, ax = plt.subplots(figsize=(8, 6))
            if st.session_state['ambas_antes_despues_' + self.plot_id] == 'Antes vs Después':
                sns.countplot(data=self.df_combinado,x=self.x, ax=ax, palette=sns.light_palette(self.color, n_colors=2), dodge=True, order=self.order, hue='Periodo')
            else:
                sns.countplot(data=self.df, x=self.x, ax=ax, color=self.color, order=self.order)
            total = sum([p.get_height() for p in ax.patches])
            for p in ax.patches:
                if p.get_height() > 0:
                    value = int(p.get_height())
                    percentage = 100 * p.get_height() / total
                    ax.annotate(f'{value} ({percentage:.1f}%)', (p.get_x() + p.get_width() / 2, p.get_height() ), ha='center', va='bottom', fontsize=self.fontsize2, color='grey', rotation = self.rotation2)
            
            ax.set_title(self.title, fontsize=20)
            ax.set_xlabel(self.x_label, fontsize=15)
            ax.set_ylabel('Frecuencia', fontsize=15)
            plt.xticks(rotation=self.rotation, ha='right')
            st.pyplot(fig)
    
    def bar_plot(self):
        fig, ax = plt.subplots(figsize=(8, 6))
        if st.session_state['ambas_antes_despues_' + self.plot_id] == 'Antes vs Después':
            sns.barplot(data=self.df_combinado, x=self.x, y=self.y, ax=ax, palette=sns.light_palette(self.color, n_colors=2), order=self.order, hue='Periodo', ci=None)
        else:
            sns.barplot(data=self.df, x=self.x, y=self.y, ax=ax, color=self.color, order=self.order, ci=None)
        total = sum([p.get_height() for p in ax.patches])
        for p in ax.patches:
            if p.get_height() > 0:
                value = int(p.get_height())
                percentage = 100 * p.get_height() / total
                ax.annotate(f'{value} ({percentage:.1f}%)', (p.get_x() + p.get_width() / 2, p.get_height() ) , ha='center', va='bottom', fontsize=self.fontsize2, color='grey', rotation = self.rotation2)
       
        ax.set_title(self.title, fontsize=20)
        ax.set_xlabel(self.x_label, fontsize=15)
        ax.set_ylabel(self.y_label, fontsize=15)
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)

    def scatter_plot(self):
        fig, ax = plt.subplots(figsize=(8, 6))
        if st.session_state['ambas_antes_despues_' + self.plot_id] == 'Antes vs Después':
            sns.scatterplot(data=self.df_combinado, x=self.x, y=self.y, ax=ax, hue='Periodo', palette=sns.light_palette(self.color, n_colors=2))
        else:
            sns.scatterplot(data=self.df, x=self.x, y=self.y, ax=ax, color=self.color)
        ax.set_title(self.title, fontsize=20)
        ax.set_xlabel(self.x_label, fontsize=15)
        ax.set_ylabel(self.y_label, fontsize=15)
        ax.yaxis.set_visible(self.y_visible)
        if self.rotation:
            plt.xticks(rotation=45)
        st.pyplot(fig)

    def box_plot(self):
        fig, ax = plt.subplots(figsize=(8, 6))
        
        if st.session_state['ambas_antes_despues_' + self.plot_id] == 'Antes vs Después':
            sns.boxplot(data=self.df_combinado, x=self.x, ax=ax, palette=sns.light_palette(self.color, n_colors=2), hue='Periodo')
        else:
            sns.boxplot(data=self.df, x=self.x, ax=ax, color=self.color)
        ax.set_title(self.title, fontsize=20)
        ax.set_xlabel(self.x_label, fontsize=15)
        ax.set_ylabel(self.y_label, fontsize=15)
        ax.yaxis.set_visible(self.y_visible)
        plt.xticks(rotation=self.rotation)
        st.pyplot(fig)
        
    def map(self): 
        layer = pdk.Layer("HeatmapLayer",data=self.df,  get_position='[Longitude, Latitude]',  opacity=0.9,  radius_pixels=100,  intensity=1,  )
        view_state = pdk.ViewState(latitude=self.df['Latitude'].mean(),  longitude=self.df['Longitude'].mean(),  zoom=5,  pitch=50  )
        tooltip = {"html": "<b>Province:</b> {provincia}<br><b>Quantity:</b> {quantity}","style": {"backgroundColor": "steelblue","color": "white"}}
        deck = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)
        st.pydeck_chart(deck)

def main():
    st.title("CSV File Upload and Data Analysis")

    # Initialize the DataLoader
    
    df_all = None  # Initialize df_all as None

    # Manually upload CSV files using the file uploader
    uploaded_before = st.file_uploader("Upload the 'Before' CSV")
    uploaded_after = st.file_uploader("Upload the 'After' CSV")
   
    data_loader = DataLoader()

    # Check if both files are uploaded
    if uploaded_before is not None and uploaded_after is not None:
        with st.spinner("Loading data..."):
            # Load the data using the DataLoader
            df_all = data_loader.load_data(uploaded_before, uploaded_after, 'Geo.csv')

        st.success("Data loaded successfully!")

    # If df_all is still None, warn the user and stop execution
    if df_all is None:
        st.warning("Please upload both CSV files to proceed.")
        return

    num_plots = st.sidebar.slider("Select the number of plots", min_value=1, max_value=9, value=1, step=1)
    if num_plots == 1:
        plots_per_row = 1
    elif num_plots == 2:
        plots_per_row = 2
    else: 
        plots_per_row = 3
    plot_count = 0  
    
    while plot_count < num_plots:
        columns = st.columns(plots_per_row)
        for col in columns:
            if plot_count < num_plots:
                plot_id = f'plot_{plot_count + 1}'  
                st.sidebar.header(f"Plot - {plot_count + 1}")  
                with st.spinner("Cargando datos y aplicando filtros, por favor espere..."):
                    streamlit_app = StreamLit(df_all, plot_id)
                    streamlit_app.sidebar()  
                    filters = Filters(df_all, plot_id)
                    filters.choose_filter()
                    df_filtered = filters.result
                    df_filtered_antes = filters.result_antes
                    df_filtered_despues = filters.result_despues
                    column_order = ['date_recepcion_data', 'user_id', 'SEGUISTE_RECOMENDACIONES', 'days_diff', 'age', 'age_category', 'genero', 'provincia', 'localidad', 'Latitude', 'Longitude', 'RECOMENDACIONES_AJUSTE', 'date_generacion_recomendacion', 'FOTICO_luz_natural_8_15_integrada', 'FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada', 'NOFOTICO_estudios_integrada', 'NOFOTICO_trabajo_integrada', 'NOFOTICO_otra_actividad_habitual_si_no', 'NOFOTICO_cena_integrada', 'HAB_Hora_acostar', 'HAB_Hora_decidir', 'HAB_min_dormir', 'HAB_Soffw', 'NOFOTICO_HAB_alarma_si_no', 'HAB_siesta_integrada', 'HAB_calidad', 'LIB_Hora_acostar', 'LIB_Hora_decidir', 'LIB_min_dormir', 'LIB_Offf', 'LIB_alarma_si_no', 'MEQ_score_total','rec_NOFOTICO_HAB_alarma_si_no', 'rec_FOTICO_luz_natural_8_15_integrada' ,'rec_FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada',	'rec_NOFOTICO_estudios_integrada', 'rec_NOFOTICO_trabajo_integrada', 'rec_NOFOTICO_otra_actividad_habitual_si_no',	'rec_NOFOTICO_cena_integrada',	'rec_HAB_siesta_integrada', 'MEQ_score_total_tipo', 'MSFsc', 'HAB_SDw', 'SJL', 'HAB_SOnw_centrado']
                    column_order_combinado = ['date_recepcion_data', 'user_id', 'SEGUISTE_RECOMENDACIONES', 'days_diff', 'Periodo' ,'age', 'age_category', 'genero', 'provincia', 'localidad', 'Latitude', 'Longitude', 'RECOMENDACIONES_AJUSTE', 'date_generacion_recomendacion', 'FOTICO_luz_natural_8_15_integrada', 'FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada', 'NOFOTICO_estudios_integrada', 'NOFOTICO_trabajo_integrada', 'NOFOTICO_otra_actividad_habitual_si_no', 'NOFOTICO_cena_integrada', 'HAB_Hora_acostar', 'HAB_Hora_decidir', 'HAB_min_dormir', 'HAB_Soffw', 'NOFOTICO_HAB_alarma_si_no', 'HAB_siesta_integrada', 'HAB_calidad', 'LIB_Hora_acostar', 'LIB_Hora_decidir', 'LIB_min_dormir', 'LIB_Offf', 'LIB_alarma_si_no', 'MEQ_score_total','rec_NOFOTICO_HAB_alarma_si_no', 'rec_FOTICO_luz_natural_8_15_integrada' ,'rec_FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada',	'rec_NOFOTICO_estudios_integrada', 'rec_NOFOTICO_trabajo_integrada', 'rec_NOFOTICO_otra_actividad_habitual_si_no',	'rec_NOFOTICO_cena_integrada',	'rec_HAB_siesta_integrada', 'MEQ_score_total_tipo', 'MSFsc', 'HAB_SDw', 'SJL', 'HAB_SOnw_centrado']
                    df_all = df_all[column_order]
                    df_filtered = df_filtered[column_order]
        
                    df_all = df_all.sort_values(by=['user_id', 'date_recepcion_data'], ascending=[True, True])
                    df_filtered = df_filtered.sort_values(by=['user_id', 'date_recepcion_data'], ascending=[True, True])
                    
                    df_filtered_antes.loc[:, 'Periodo'] = 'Antes'
                    df_filtered_despues.loc[:, 'Periodo'] = 'Después'
                    df_filtered_antes = df_filtered_antes.reset_index(drop=True)
                    df_filtered_despues = df_filtered_despues.reset_index(drop=True)
                    df_combinado = pd.concat([df_filtered_antes, df_filtered_despues], ignore_index=False)
                    df_combinado = df_combinado.reset_index(drop=True)
                    df_combinado = df_combinado[column_order_combinado]
                    df_combinado = df_combinado.sort_values(by=['user_id', 'date_recepcion_data'], ascending=[True, True])
                    with col:  
                        if st.session_state['datos_' + plot_id] == False:                    
                            
                            st.write('Datos')
                            if st.session_state['ambas_antes_despues_' + plot_id] == 'Antes vs Después':   
                                st.write(f'Cantidad : {len(df_combinado)}')  
                                st.write(df_combinado)
                            else:
                                st.write(f'Cantidad : {len(df_filtered)}')  
                                st.write(df_filtered)  
                        plot_generator = PlotGenerator(df_filtered, df_combinado, plot_id) 
                        plot_generator.choose_plot()  

                    plot_count += 1  

main()


#streamlit run '/Users/tomasmendietarios/Library/Mobile Documents/com~apple~CloudDocs/I.T.B.A/MRI/main.py'