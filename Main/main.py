import numpy as np
import pandas as pd
import streamlit as st
import seaborn as sb
import matplotlib.pyplot as plt
import pydeck as pdk

# Define the main StreamlitApp class
class DataLoader:
    
    def __init__(self):
        self.df_all = pd.DataFrame()
        
    def load_data(self, before_path, after_path):
        df_before = pd.read_csv(before_path)
        df_after = pd.read_csv(after_path)
        self.df_all = pd.concat([df_before, df_after], ignore_index=True)
        self.df_all['date_recepcion_data'] = pd.to_datetime(self.df_all['date_recepcion_data'])
        self.df_all.sort_values(by=['user_id', 'date_recepcion_data'], ascending=[True, True], inplace=True)
        self.df_all.reset_index(drop=True, inplace=True)
        self.df_all['days_diff'] = self.df_all.groupby('user_id')['date_recepcion_data'].diff().dt.days.fillna(0)
        return self.df_all

class StreamLit:
    
    def __init__(self, df):
        self.df_all = df
        self.initialize_filters()
   
    def sidebar(self):
        st.sidebar.header('Filter Options')
        
        st.sidebar.selectbox("Entrada Usuarios", options=["Entradas", "Usuarios"], key='entradas_usuarios_filter')

        st.sidebar.checkbox("All Dates",  key='all_dates_checkbox')
        if not st.session_state['all_dates_checkbox']:
            st.sidebar.date_input("Start Date", value=self.df_all['date_recepcion_data'].min(), key='start_date_input')
            st.sidebar.date_input("End Date", value=self.df_all['date_recepcion_data'].max(), key='end_date_input')

        st.sidebar.checkbox("All Ages", key='all_ages_checkbox')
        if not st.session_state['all_ages_checkbox']:
            st.sidebar.slider("Age Range", min_value=int(self.df_all['age'].min()),max_value=int(self.df_all['age'].max()),value=(int(self.df_all['age'].min()), int(self.df_all['age'].max())),key='age_range_slider')

        st.sidebar.checkbox("All Genders",  key='all_genders_checkbox')
        if not st.session_state['all_genders_checkbox']:
            st.sidebar.selectbox("Select Gender", options=self.df_all['genero'].unique().tolist(), key='gender_selectbox')

        st.sidebar.checkbox("All Recommendations", key='all_recommendations_checkbox')
        if not st.session_state['all_recommendations_checkbox']:
            st.sidebar.selectbox("Seguiste recomendaciones", options=['Si', 'No', 'Ambas'], key='recommendations_selectbox')
            st.sidebar.number_input("Min days difference", min_value=0, max_value=100, key='min_days_diff_input')
            st.sidebar.number_input("Max days difference", min_value=0, max_value=100, key='max_days_diff_input')
            st.sidebar.selectbox("Ambas Antes Después", options=["Ambas", "Antes", "Después"], key='ambas_antes_despues')

        st.sidebar.checkbox("Categorize Ages",  key='categorize_ages_checkbox')
        if st.session_state['categorize_ages_checkbox']:
            st.sidebar.subheader("Define Age Categories")
            st.sidebar.slider("Min Age for Jóvenes", min_value=0, max_value=100,  key='age_joven_min_slider')
            st.sidebar.slider("Min Age for Adultos", min_value=0, max_value=100, value=30, key='age_adult_min_slider')
            st.sidebar.slider("Min Age for Tercera Edad", min_value=0, max_value=100, value=60, key='age_tercera_edad_min_slider')
       
        st.sidebar.title('Plotting Options')
        st.sidebar.selectbox("Choose plot type", ["Histogram", "Scatter", "Bar", "Line", "Box"])
        st.sidebar.selectbox("Choose plot ", ["date_recepcion_data", "Scatter", "Bar", "Line", "Box"])
        
        
    def initialize_filters(self):
        if 'age_range_slider' not in st.session_state:
            st.session_state['age_range_slider'] = [self.df_all['age'].min(), self.df_all['age'].max()]
        if 'selected_gender' not in st.session_state:
            st.session_state['selected_gender'] = 'All'
        if 'df_selected' not in st.session_state:
            st.session_state['df_selected'] = self.df_all
        if 'recommendations_selectbox' not in st.session_state:
            st.session_state['recommendations_selectbox'] = 'Ambas'
        if 'min_days_diff_input' not in st.session_state:
            st.session_state['min_days_diff_input'] = 0
        if 'max_days_diff_input' not in st.session_state:
            st.session_state['max_days_diff_input'] = 30
        
        if 'categorize_ages_checkbox' not in st.session_state:
            st.session_state['categorize_ages_checkbox'] = False
        if 'age_joven_min_slider' not in st.session_state:
            st.session_state['age_joven_min_slider'] = 13
        if 'age_adult_min_slider' not in st.session_state:
            st.session_state['age_adult_min_slider'] = 60
        if 'age_tercera_edad_min_slider' not in st.session_state:
            st.session_state['age_tercera_edad_min_slider'] = 60 
        
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

        if st.session_state['categorize_ages_checkbox']:  
            self.categorize_age()
            
        if not st.session_state['all_genders_checkbox']:  
            self.genders()
        
        if not st.session_state['all_recommendations_checkbox']:  
            self.recomendations()
        
        if st.session_state['entradas_usuarios_filter'] == 'Usuarios':
            self.entries_users()
        

        return self.result
            
class PlotGenerator():
    def __init__(self,df):
        self.df_all = df
    
       
    

        
        
def main():
    data_loader = DataLoader()
    df_all = data_loader.load_data('Data/allData_MiRelojInterno_24Julio2024.csv', 'Data/allData_MiRelojInterno_27Marzo2023.csv')
    
    streamlit_app = StreamLit(df_all)
    streamlit_app.sidebar()
    
    filters = Filters(df_all)
    df_filtered = filters.choose_filter()  
    df_filtered = filters.result  
   
    column_order = ['date_recepcion_data', 'user_id', 'SEGUISTE_RECOMENDACIONES','days_diff','age', 'genero', 'provincia', 'localidad','RECOMENDACIONES_AJUSTE', 'date_generacion_recomendacion','FOTICO_luz_natural_8_15_integrada', 'FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada','NOFOTICO_estudios_integrada', 'NOFOTICO_trabajo_integrada', 'NOFOTICO_otra_actividad_habitual_si_no','NOFOTICO_cena_integrada', 'HAB_Hora_acostar', 'HAB_Hora_decidir', 'HAB_min_dormir', 'HAB_Soffw','NOFOTICO_HAB_alarma_si_no', 'HAB_siesta_integrada', 'HAB_calidad', 'LIB_Hora_acostar', 'LIB_Hora_decidir','LIB_min_dormir', 'LIB_Offf', 'LIB_alarma_si_no', 'MEQ1', 'MEQ2', 'MEQ3', 'MEQ4', 'MEQ5', 'MEQ6', 'MEQ7','MEQ8', 'MEQ9', 'MEQ10', 'MEQ11', 'MEQ12', 'MEQ13', 'MEQ14', 'MEQ15', 'MEQ16', 'MEQ17', 'MEQ18', 'MEQ19','rec_NOFOTICO_HAB_alarma_si_no', 'rec_FOTICO_luz_natural_8_15_integrada', 'rec_FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada','rec_NOFOTICO_estudios_integrada', 'rec_NOFOTICO_trabajo_integrada', 'rec_NOFOTICO_otra_actividad_habitual_si_no','rec_NOFOTICO_cena_integrada', 'rec_HAB_siesta_integrada', 'MEQ_score_total', 'MSFsc', 'HAB_SDw', 'SJL', 'HAB_SOnw_centrado']
    
    df_filtered = df_filtered[column_order]
    df_filtered = df_filtered.sort_values(by=['user_id', 'date_recepcion_data'], ascending=[True, True])
   
    
    df_all = df_all[column_order]
    df_all = df_all.sort_values(by=['user_id', 'date_recepcion_data'], ascending=[True, True])
    
    st.write('df_all')
    st.write(f'Cantidad de usuarios: {len(df_all)}')  
    st.write(df_all)
    
    st.write('Data filtrada')
    st.write(f'Cantidad de usuarios: {len(df_filtered)}')  
    st.write(df_filtered)

main()

# streamlit run '/Users/tomasmendietarios/Library/Mobile Documents/com~apple~CloudDocs/I.T.B.A/MRI/Main/main.py'





