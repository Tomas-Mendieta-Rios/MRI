import numpy as np
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pydeck as pdk
import plotly.express as px
import seaborn.objects as so
st.set_page_config(layout="wide")

data_dictionary = {
    'Fecha de recepción de datos': 'date_recepcion_data',
    'ID de usuario': 'user_id',
    'Edad': 'age',
    'Género': 'genero',
    'Provincia': 'provincia',
    'Localidad': 'localidad',
    'Fecha de generación de recomendación': 'date_generacion_recomendacion',
    'Seguiste recomendaciones': 'SEGUISTE_RECOMENDACIONES',
    'Percepción de cambio': 'RECOMENDACIONES_AJUSTE',
    'Exposición luz natural': 'FOTICO_luz_natural_8_15_integrada',
    'Exposición luz artificial': 'FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada',
    'Estudios no foticos integrados': 'NOFOTICO_estudios_integrada',
    'Trabajo no fotico integrado': 'NOFOTICO_trabajo_integrada',
    'Otra actividad habitual no fotica': 'NOFOTICO_otra_actividad_habitual_si_no',
    'Cena no fotica integrada': 'NOFOTICO_cena_integrada',
    'Horario de acostarse (habitual)': 'HAB_Hora_acostar',
    'Horario decidir dormir (habitual)': 'HAB_Hora_decidir',
    'Minutos dormir (habitual)': 'HAB_min_dormir',
    'Hora despertar (habitual)': 'HAB_Soffw',
    'Alarma no fotica (sí/no)': 'NOFOTICO_HAB_alarma_si_no',
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

keys = list(data_dictionary.keys())

caracteristicas = {'Edad':'age', 'Genero':'genero', 'Ubicación': 'provincia', 'Fecha' : 'date_generacion_recomendacion'}
recomendaciones = {'Seguiste recomendaciones': 'SEGUISTE_RECOMENDACIONES', 'Percepción de cambio':'RECOMENDACIONES_AJUSTE'}
exposicion_luz = {'Exposición luz natural':'FOTICO_luz_natural_8_15_integrada','Exposición luz artifical':'FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada'}
plot_sleep = {'Horario de acostarse': 'HAB_Hora_acostar', 'Horario decidir dormir':'HAB_Hora_decidir', 'Minutos dormir': 'HAB_min_dormir', 'Hora Despertarse': 'HAB_Soffw'}

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
            st.sidebar.selectbox("Seguiste recomendaciones", options=['Si', 'No', 'Ambas'], key='recommendations_selectbox')
            st.sidebar.number_input("Min days difference", min_value=0, max_value=100, key='min_days_diff_input')
            st.sidebar.number_input("Max days difference", min_value=0, max_value=1000, key='max_days_diff_input')
            st.sidebar.selectbox("Ambas Antes Después", options=["Ambas", "Antes", "Después"], key='ambas_antes_despues')

        st.sidebar.subheader("Define Age Categories")
        st.sidebar.slider("Min Age for Jóvenes", min_value=0, max_value=100,  key='age_joven_min_slider')
        st.sidebar.slider("Min Age for Adultos", min_value=0, max_value=100,  key='age_adult_min_slider')
        st.sidebar.slider("Min Age for Tercera Edad", min_value=0, max_value=100,  key='age_tercera_edad_min_slider')
        
        #st.sidebar.title('Gráficos')
        #st.sidebar.selectbox('Características usuarios', ['Edad', 'Género', 'Provincia', 'Fecha de generación de recomendación'], key='plot')
        #st.sidebar.selectbox('Recomendaciones', ['Seguiste recomendaciones', 'Percepción de cambio'], key='plot')
        #st.sidebar.selectbox("Exposición a la luz", ['Exposición luz natural', 'Exposición luz artificial'], key='plot')
        st.sidebar.selectbox("Sueño", list(data_dictionary.keys()), key='plot')
        st.sidebar.checkbox("Mostrar datos", key='datos')
       
        
    def initialize_filters(self):
        
        if 'datos' not in st.session_state:
            st.session_state['datos'] = True
            
        if 'age_range_slider' not in st.session_state:
            st.session_state['age_range_slider'] = [self.df['age'].min(), self.df['age'].max()]

        if 'selected_gender' not in st.session_state:
            st.session_state['selected_gender'] = 'All'

        if 'df_selected' not in st.session_state:
            st.session_state['df_selected'] = self.df

        if 'recommendations_selectbox' not in st.session_state:
            st.session_state['recommendations_selectbox'] = 'Ambas'

        if 'min_days_diff_input' not in st.session_state:
            st.session_state['min_days_diff_input'] = 0

        if 'max_days_diff_input' not in st.session_state:
            st.session_state['max_days_diff_input'] = 30

        if 'age_joven_min_slider' not in st.session_state:
            st.session_state['age_joven_min_slider'] = 13

        if 'age_adult_min_slider' not in st.session_state:
            st.session_state['age_adult_min_slider'] = 40

        if 'age_tercera_edad_min_slider' not in st.session_state:
            st.session_state['age_tercera_edad_min_slider'] = 70

        if 'antes_despues' not in st.session_state:
            st.session_state['antes_despues'] = 'Ambas'

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
        
        if 'plot' not in st.session_state:
            st.session_state['plot'] = 'Exposición luz natural'

        
class Filters:
    def __init__(self,df):
        self.df_all = df
        self.result = df
    
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
            if age < st.session_state['age_adult_min_slider']:
                return 'Jóvenes'
            elif age < st.session_state['age_tercera_edad_min_slider']:
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

        if st.session_state['age_joven_min_slider'] or st.session_state['age_adult_min_slider'] or st.session_state['age_tercera_edad_min_slider'] :  
            self.categorize_age()
            
        if not st.session_state['all_genders_checkbox']:  
            self.genders()
        
        if not st.session_state['all_recommendations_checkbox']:  
            self.recomendations()
        
        if st.session_state['entradas_usuarios_filter'] == 'Usuarios':
            self.entries_users()

        return self.result
            
class PlotGenerator:
    def __init__(self,df):
        self.df = df
        self.xtick = []
        self.xtick_labels = []
        
    def choose_plot(self):
        
        if st.session_state['plot'] == 'Edad':
            self.gauss()
        if st.session_state['plot'] == 'Exposición luz natural':
            self.xtick = [0,1,2]
            self.xtick_labels = ['0','1','2']
            self.histo_plot()
        elif st.session_state['plot'] == "Exposición luz artificial":
            self.xtick = [0,1]
            self.xtick_labels = ['0','1']
            self.histo_plot()
        elif st.session_state['plot'] == "Otra actividad habitual no fotica":
            self.xtick = [0,1]
            self.xtick_labels = ['0','1']
            self.histo_plot()
        elif st.session_state['plot'] == "Estudios no foticos integrados":
            self.xtick = [-1,0,1]
            self.xtick_labels = ['-1','0','1']
            self.histo_plot()
        elif st.session_state['plot'] == "Provincia":
            self.map()

    def gauss(self):

        # Histogram without 'genero'
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.histplot(data=self.df, x='age', kde=False, bins=20, ax=ax)
        ax.set_title('Age Distribution', fontsize=20)
        ax.set_xlabel('Age', fontsize=15)
        ax.set_ylabel('Count', fontsize=15)
        st.pyplot(fig)

        # KDE plot without 'genero'
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.kdeplot(data=self.df, x='age', ax=ax, fill=True)
        ax.set_title('Age Distribution (KDE)', fontsize=20)
        ax.set_xlabel('Age', fontsize=15)
        ax.set_ylabel('Density', fontsize=15)
        st.pyplot(fig)


        # Box plot without 'genero'
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.boxplot(data=self.df, x='age', ax=ax)
        ax.set_title('Age Distribution (Box Plot)', fontsize=20)
        ax.set_xlabel('Age', fontsize=15)
        st.pyplot(fig)


        # Violin plot without 'genero'
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.violinplot(data=self.df, x='age', ax=ax)
        ax.set_title('Age Distribution (Violin Plot)', fontsize=20)
        ax.set_xlabel('Age', fontsize=15)
        st.pyplot(fig)


    # Column 2: Plots with 'genero' hue

        # Histogram with 'genero'
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.histplot(data=self.df, x='age', hue='genero', kde=False, bins=20, multiple='dodge', ax=ax)
        ax.set_title('Age Distribution by Genero', fontsize=20)
        ax.set_xlabel('Age', fontsize=15)
        ax.set_ylabel('Count', fontsize=15)
        st.pyplot(fig)


        # KDE plot with 'genero'
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.kdeplot(data=self.df, x='age', hue='genero', ax=ax, fill=True)
        ax.set_title('Age Distribution (KDE) by Genero', fontsize=20)
        ax.set_xlabel('Age', fontsize=15)
        ax.set_ylabel('Density', fontsize=15)
        st.pyplot(fig)


        # Box plot with 'genero'
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.boxplot(data=self.df, x='genero', y='age', ax=ax)
        ax.set_title('Age Distribution by Genero (Box Plot)', fontsize=20)
        ax.set_xlabel('Genero', fontsize=15)
        ax.set_ylabel('Age', fontsize=15)
        st.pyplot(fig)


        # Violin plot with 'genero'
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.violinplot(data=self.df, x='genero', y='age', ax=ax)
        ax.set_title('Age Distribution by Genero (Violin Plot)', fontsize=20)
        ax.set_xlabel('Genero', fontsize=15)
        ax.set_ylabel('Age', fontsize=15)
        st.pyplot(fig)
   


        
    def histo_plot(self):
        
        st.markdown(f"<h1 style='font-size:40px;'>{st.session_state['plot']}</h1>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            fig1, ax1 = plt.subplots(figsize=(8, 6))
            sns.histplot(data=self.df, x=data_dictionary[st.session_state['plot']], kde=False, discrete=True, ax=ax1)
            ax1.set_xlabel('')
            ax1.set_ylabel('')
            ax1.set_xticks(self.xtick)
            st.pyplot(fig1)

        # Plot 2 - Histogram with hue for 'genero'
        with col2:
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            sns.histplot(
                data=self.df,
                x=data_dictionary[st.session_state['plot']],
                hue='genero',
                kde=False,
                discrete=True,
                bins=len(self.xtick),
                shrink=0.8,
                ax=ax2,
                multiple='dodge'
            )
            ax2.set_title('')
            ax2.set_xlabel('')
            ax2.set_ylabel('')
            ax2.set_xticks(self.xtick)
            ax2.set_xticklabels(self.xtick_labels)
            ax2.tick_params(axis='x')
            ax2.tick_params(axis='y')
            plt.tight_layout()
            st.pyplot(fig2)

     
        
        g = sns.FacetGrid(
        self.df,
        col="age_category",  # Separate columns for each age category
        height=5,
        aspect=1.2,
        margin_titles=True
        )

        # Use map_dataframe to plot histograms, with 'genero' as the hue and count on y-axis
        g.map_dataframe(
            sns.histplot,
            x=data_dictionary[st.session_state['plot']],
            hue="genero",
            multiple="dodge",
            shrink=0.8,
            discrete=True
        )

        # Add a legend to differentiate the genders
        g.add_legend()

        # Set common labels and titles
        
        g.set_axis_labels('', '')  # Adjust the labels as needed
        g.set_titles(col_template='{col_name}')
        for ax in g.axes.flat:
            ax.set_xticks(self.xtick)
            ax.set_xticklabels(self.xtick_labels)
            ax.tick_params(axis='y')

        plt.tight_layout()
        st.pyplot(g)
        

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
    if  st.session_state['datos'] == False:  
        st.write('df_all')
        st.write(f'Cantidad de usuarios: {len(df_all)}')  
        st.write(df_all)
        
        st.write('Data filtrada')
        st.write(f'Cantidad de usuarios: {len(df_filtered)}')  
        st.write(df_filtered)

    plot_generator = PlotGenerator(df_filtered)
    plot_generator.choose_plot()

main()

# streamlit run '/Users/tomasmendietarios/Library/Mobile Documents/com~apple~CloudDocs/I.T.B.A/MRI/Main/main.py'






