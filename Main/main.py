# Importing necessary libraries
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

# Define the main StreamlitApp class
class StreamlitApp:
    def __init__(self):
        self.df_all = pd.DataFrame()
        self.setup()
        self.initialize_filters()

    def setup(self):
        # Load two CSV datasets, one before and one after a certain date
        df_before = pd.read_csv('/Users/tomasmendietarios/Library/Mobile Documents/com~apple~CloudDocs/I.T.B.A/MRI/Data/allData_MiRelojInterno_27Marzo2023.csv')
        df_after = pd.read_csv('/Users/tomasmendietarios/Library/Mobile Documents/com~apple~CloudDocs/I.T.B.A/MRI/Data/allData_MiRelojInterno_24Julio2024.csv')
        
        # Concatenate both datasets into one, ignoring index to avoid duplicate indices
        self.df_all = pd.concat([df_before, df_after], ignore_index=True)
        
        # Convert 'date_recepcion_data' column to datetime format and sort the data by user_id and date
        self.df_all['date_recepcion_data'] = pd.to_datetime(self.df_all['date_recepcion_data'])
        self.df_all.sort_values(by=['user_id', 'date_recepcion_data'], ascending=[True, True], inplace=True)
        self.df_all.reset_index(drop=True, inplace=True)
        
        # Calculate the difference in days between consecutive entries for the same user
        self.df_all['days_diff'] = self.df_all.groupby('user_id')['date_recepcion_data'].diff().dt.days.fillna(0)
        
        # Save the processed data to a CSV file for further use
        self.df_all.to_csv('/Users/tomasmendietarios/Library/Mobile Documents/com~apple~CloudDocs/I.T.B.A/MRI/Data/All.csv')

    def initialize_filters(self):
        """
        Initialize session state variables used for filtering and categorizing data in the app.
        """
        # Set default values for the session state variables if not already defined
        if 'date_min' not in st.session_state:
            st.session_state.date_min = self.df_all['date_recepcion_data'].min()
        if 'date_max' not in st.session_state:
            st.session_state.date_max = self.df_all['date_recepcion_data'].max()
        if 'age' not in st.session_state:
            st.session_state.age = [self.df_all['age'].min(), self.df_all['age'].max()]
        if 'selected_gender' not in st.session_state:
            st.session_state.selected_gender = 'All'
        if 'df_selected' not in st.session_state:
            st.session_state.df_selected = self.df_all
        if 'selected_recomendaciones' not in st.session_state:
            st.session_state.selected_recomendaciones = 'ambas'
        if 'selected_recomendaciones_rango_min' not in st.session_state:
            st.session_state.selected_recomendaciones_rango_min = 0
        if 'selected_recomendaciones_rango_max' not in st.session_state:
            st.session_state.selected_recomendaciones_rango_max = 30
        if 'categorize_ages' not in st.session_state:
            st.session_state.categorize_ages = False  # Default value for whether to categorize ages or not
        if 'antes_despues' not in st.session_state:
            st.session_state.antes_despues = 'Ambas'  # Default value for whether to categorize ages or not

    def apply_filters(self):
        df_filtered = self.df_all

        # Check if the filter for 'Entradas' or 'Usuarios' is set
        if st.session_state['entradas_usuarios'] == 'Usuarios':
            df_filtered = df_filtered.drop_duplicates(subset='user_id', keep='last')

        # Apply date filters if 'All Dates' is not selected
        if not st.session_state.get('all_dates', True):
            date_min = pd.to_datetime(st.session_state['date_min'])
            date_max = pd.to_datetime(st.session_state['date_max'])
            df_filtered = df_filtered[(df_filtered['date_recepcion_data'] >= date_min) & (df_filtered['date_recepcion_data'] <= date_max)]

        # Apply age filters if 'All Ages' is not selected
        if not st.session_state.get('all_ages', True):
            age_min, age_max = st.session_state['age']
            df_filtered = df_filtered[(df_filtered['age'] >= age_min) & (df_filtered['age'] <= age_max)]

        # Apply gender filters if a specific gender is selected
        if st.session_state.get('selected_gender', 'All') != 'All':
            df_filtered = df_filtered[df_filtered['genero'] == st.session_state['selected_gender']]

        if st.session_state.get('selected_recomendaciones', 'All') != 'All':
            # Retrieve session state values
            days_min = st.session_state['selected_recomendaciones_rango_min']
            days_max = st.session_state['selected_recomendaciones_rango_max']
            rec_filter = st.session_state['selected_recomendaciones']
            when_filter = st.session_state['ambas_antes_despues']
            
            # Sort and reset index to have a clean sequential index
            df_filtered = df_filtered.sort_values(by=['user_id', 'date_recepcion_data'], ascending=[True, True])
            df_filtered = df_filtered.reset_index(drop=True)
            
            # Initialize list to store final indices
            final_indices = []

            # Apply filtering based on recommendation ("Si" or "No")
            for idx in range(1, len(df_filtered)):  # Start from 1 to avoid out-of-bounds for idx-1
                if df_filtered.loc[idx - 1, 'user_id'] == df_filtered.loc[idx, 'user_id']:
                    # Check for both 'si' and 'no' recommendations if 'ambas' is selected
                    if rec_filter == 'ambas':
                        if df_filtered.loc[idx, 'SEGUISTE_RECOMENDACIONES'] in ['si', 'no']:
                            if days_min <= df_filtered.loc[idx, 'days_diff'] <= days_max:
                                if when_filter == 'Ambas':
                                    final_indices.append(idx - 1)
                                    final_indices.append(idx)
                                elif when_filter == 'Antes':
                                    final_indices.append(idx - 1)
                                elif when_filter == 'Después':
                                    final_indices.append(idx)

                    # Filter for 'si' recommendations
                    elif rec_filter == 'si' and df_filtered.loc[idx, 'SEGUISTE_RECOMENDACIONES'] == 'si':
                        if days_min <= df_filtered.loc[idx, 'days_diff'] <= days_max:
                            if when_filter == 'Ambas':
                                final_indices.append(idx - 1)
                                final_indices.append(idx)
                            elif when_filter == 'Antes':
                                final_indices.append(idx - 1)
                            elif when_filter == 'Después':
                                final_indices.append(idx)

                    # Filter for 'no' recommendations
                    elif rec_filter == 'no' and df_filtered.loc[idx, 'SEGUISTE_RECOMENDACIONES'] == 'no':
                        if days_min <= df_filtered.loc[idx, 'days_diff'] <= days_max:
                            if when_filter == 'Ambas':
                                final_indices.append(idx - 1)
                                final_indices.append(idx)
                            elif when_filter == 'Antes':
                                final_indices.append(idx - 1)
                            elif when_filter == 'Después':
                                final_indices.append(idx)
            
            # Filter the DataFrame based on the indices
            df_filtered = df_filtered.loc[final_indices].reset_index(drop=True)


        # Store the filtered DataFrame in the session state
        column_order = [
        'date_recepcion_data', 'user_id', 'SEGUISTE_RECOMENDACIONES','days_diff','age', 'genero', 'provincia', 'localidad',
         'RECOMENDACIONES_AJUSTE', 'date_generacion_recomendacion',
        'FOTICO_luz_natural_8_15_integrada', 'FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada',
        'NOFOTICO_estudios_integrada', 'NOFOTICO_trabajo_integrada', 'NOFOTICO_otra_actividad_habitual_si_no',
        'NOFOTICO_cena_integrada', 'HAB_Hora_acostar', 'HAB_Hora_decidir', 'HAB_min_dormir', 'HAB_Soffw',
        'NOFOTICO_HAB_alarma_si_no', 'HAB_siesta_integrada', 'HAB_calidad', 'LIB_Hora_acostar', 'LIB_Hora_decidir',
        'LIB_min_dormir', 'LIB_Offf', 'LIB_alarma_si_no', 'MEQ1', 'MEQ2', 'MEQ3', 'MEQ4', 'MEQ5', 'MEQ6', 'MEQ7',
        'MEQ8', 'MEQ9', 'MEQ10', 'MEQ11', 'MEQ12', 'MEQ13', 'MEQ14', 'MEQ15', 'MEQ16', 'MEQ17', 'MEQ18', 'MEQ19',
        'rec_NOFOTICO_HAB_alarma_si_no', 'rec_FOTICO_luz_natural_8_15_integrada', 'rec_FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada',
        'rec_NOFOTICO_estudios_integrada', 'rec_NOFOTICO_trabajo_integrada', 'rec_NOFOTICO_otra_actividad_habitual_si_no',
        'rec_NOFOTICO_cena_integrada', 'rec_HAB_siesta_integrada', 'MEQ_score_total', 'MSFsc', 'HAB_SDw', 'SJL', 'HAB_SOnw_centrado'
         ]
        df = self.df_all [column_order]
        df = df.sort_values(by=['user_id', 'date_recepcion_data'], ascending=[True, True])
        st.write(df)
        df_filtered = df_filtered[column_order]
        df_filtered = df_filtered.sort_values(by=['user_id', 'date_recepcion_data'], ascending=[True, True])
        st.session_state['df_selected'] = df_filtered
 

    def display_sidebar(self):

        st.sidebar.header('Filter Options')

        # Filtro para seleccionar si mostrar todas las entradas o solo los usuarios
        st.sidebar.selectbox("Entrada Usuarios", options=["Entradas", "Usuarios"], key='entradas_usuarios')

        # Filtro por fechas
        st.session_state.all_dates = st.sidebar.checkbox("All Dates", value=True, key='all_dates_checkbox')
        if not st.session_state.all_dates:
            st.session_state.date_min = st.sidebar.date_input("Start Date", value=self.df_all['date_recepcion_data'].min(), key='start_date_input')
            st.session_state.date_max = st.sidebar.date_input("End Date", value=self.df_all['date_recepcion_data'].max(), key='end_date_input')
        else:
            st.session_state.date_min = self.df_all['date_recepcion_data'].min()
            st.session_state.date_max = self.df_all['date_recepcion_data'].max()

        # Filtro por edades
        st.session_state.all_ages = st.sidebar.checkbox("All Ages", value=True, key='all_ages_checkbox')
        if not st.session_state.all_ages:
            st.session_state.age = st.sidebar.slider(
                "Age Range",
                min_value=int(self.df_all['age'].min()),
                max_value=int(self.df_all['age'].max()),
                value=(int(self.df_all['age'].min()), int(self.df_all['age'].max())),
                key='age_range_slider'
            )
        else:
            st.session_state.age = [self.df_all['age'].min(), self.df_all['age'].max()]

        # Filtro por género
        st.session_state.all_genders = st.sidebar.checkbox("All Genders", value=True, key='all_genders_checkbox')
        if not st.session_state.all_genders:
            st.session_state.selected_gender = st.sidebar.selectbox("Select Gender", options=self.df_all['genero'].unique().tolist(), key='gender_selectbox')
        else:
            st.session_state.selected_gender = 'All'

        # Filtro por recomendaciones
        st.session_state.all_recomendaciones = st.sidebar.checkbox("All Recommendations", value=True, key='all_recommendations_checkbox')
        if not st.session_state.all_recomendaciones:
            st.session_state.selected_recomendaciones = st.sidebar.selectbox("Seguiste recomendaciones", options=['si', 'no', 'ambas'], key='recommendations_selectbox')
            st.session_state.selected_recomendaciones_rango_min = st.sidebar.number_input("Min days difference", min_value=0, max_value=100, value=st.session_state.selected_recomendaciones_rango_min, key='min_days_diff_input')
            st.session_state.selected_recomendaciones_rango_max = st.sidebar.number_input("Max days difference", min_value=0, max_value=100, value=st.session_state.selected_recomendaciones_rango_max, key='max_days_diff_input')
            st.session_state.antes_despues = st.sidebar.selectbox("Ambas Antes Después", options=["Ambas", "Antes", "Después"], key='ambas_antes_despues')

        else:
            st.session_state.selected_recomendaciones = 'All'
            st.session_state.selected_recomendaciones_rango_min = 0
            st.session_state.selected_recomendaciones_rango_max = 30

        # Filtro para la categorización por edad
        st.session_state.categorize_ages = st.sidebar.checkbox("Categorize Ages", value=st.session_state.categorize_ages, key='categorize_ages_checkbox')

        if st.session_state.categorize_ages:
            st.sidebar.subheader("Define Age Categories")
            st.session_state.age_joven_min = st.sidebar.slider("Min Age for Jóvenes", min_value=0, max_value=100, value=15, key='age_joven_min_slider')
            st.session_state.age_adult_min = st.sidebar.slider("Min Age for Adultos", min_value=0, max_value=100, value=30, key='age_adult_min_slider')
            st.session_state.age_tercera_edad_min = st.sidebar.slider("Min Age for Tercera Edad", min_value=0, max_value=100, value=60, key='age_tercera_edad_min_slider')

        # Plot type selection
        st.session_state.plot_type = st.sidebar.selectbox(
            "Select Plot Type",
            options=[
                "Distribution of Gender",
                "Distribution of Recommendations",
                "Days Difference Histogram",
                "Exposición a la luz"
            ],
            key='plot_type_selectbox'
        )

        # Apply filters button
        if st.sidebar.button("Apply Filters", key='apply_filters_button'):
            self.apply_filters()

    def categorize_age(self, df_filtered):
        """
        Categorize the age into different groups based on user-defined ranges (Jóvenes, Adultos, Tercera Edad).
        """
        # Function to categorize age based on the input age ranges
        def age_category(age):
            if age < st.session_state.age_adult_min:
                return 'Jóvenes'
            elif age < st.session_state.age_tercera_edad_min:
                return 'Adultos'
            else:
                return 'Tercera Edad'

        # Apply the age categorization to the filtered DataFrame
        df_filtered['age_category'] = df_filtered['age'].apply(age_category)

    def FOTICO_luz_natural_8_15_integrada(self):
        """
        Create and display a histogram for 'FOTICO_luz_natural_8_15_integrada' with gender as color and age category as facets.
        """
        # Ensure 'age_category' exists in the filtered DataFrame before plotting
        if 'age_category' not in st.session_state.df_selected.columns and st.session_state.categorize_ages:
            self.categorize_age(st.session_state.df_selected)

        # Create an interactive histogram using Plotly with stacked bars for genders and age categories
        fig = px.histogram(
            st.session_state.df_selected, 
            x='FOTICO_luz_natural_8_15_integrada', 
            color='genero',  # Use color to differentiate between genders
            barmode='stack',  # Stack the bars to show cumulative counts
            nbins=3,  # Define the number of bins
            facet_col='age_category' if 'age_category' in st.session_state.df_selected.columns else None,  # Add sub-hue for age category if available
            category_orders={"age_category": ["Jóvenes", "Adultos", "Tercera Edad"],  # Specify the order of age categories
                             "FOTICO_luz_natural_8_15_integrada": [0, 1, 2]}, 
            title='Exposición a la luz natural'
        )

        # Remove redundant annotations for a cleaner display
        fig.for_each_annotation(lambda a: a.update(text=a.text.replace(" FOTICO_luz_natural_8_15_integrada", "")))
        fig.for_each_annotation(lambda a: a.update(text=a.text.replace("FOTICO_luz_natural_8_15_integrada", "")))
        fig.for_each_annotation(lambda a: a.update(text=a.text.replace("age_category=", "")))

        # Update layout for improved readability
        fig.update_layout(
            xaxis=dict(tickmode='array', tickvals=[0, 1, 2], ticktext=['0', '1', '2']),  # Customize x-axis labels
            yaxis_title='Cantidad de usuarios',  # Label for the y-axis
            legend_title_text='Género'  # Legend title
        )

        # Display the chart in Streamlit
        st.plotly_chart(fig)

    def FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada(self):
        """
        Create and display a histogram for 'FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada' with gender as color and age category as facets.
        """
        # Ensure 'age_category' exists in the filtered DataFrame before plotting
        if 'age_category' not in st.session_state.df_selected.columns and st.session_state.categorize_ages:
            self.categorize_age(st.session_state.df_selected)

        # Create an interactive histogram using Plotly with stacked bars for genders and age categories
        fig = px.histogram(
            st.session_state.df_selected, 
            x='FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada', 
            color='genero',  # Use color to differentiate between genders
            barmode='stack',  # Stack the bars to show cumulative counts
            nbins=2,  # Ensure only 0 and 1 are shown on the x-axis
            facet_col='age_category' if 'age_category' in st.session_state.df_selected.columns else None,  # Add sub-hue for age category if available
            category_orders={
                "age_category": ["Jóvenes", "Adultos", "Tercera Edad"],  # Specify the order of age categories
                "FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada": [0, 1]  # Only show 0 and 1 on the x-axis
            }, 
            title='Exposición a la luz artificial'
        )

        # Remove unwanted annotations for a cleaner display
        fig.for_each_annotation(lambda a: a.update(text=a.text.replace("FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada", "")))
        fig.for_each_annotation(lambda a: a.update(text=a.text.replace("age_category=", "")))

        # Update layout for improved readability
        fig.update_layout(
            xaxis=dict(tickmode='array', tickvals=[0, 1], ticktext=['0', '1']),  # Customize x-axis to show only 0 and 1
            yaxis_title='Cantidad de usuarios',  # Label for the y-axis
            xaxis_title='',  # Hide long variable name on the x-axis
            legend_title_text='Género'  # Legend title
        )

        # Display the chart in Streamlit
        st.plotly_chart(fig)

    def display_data_and_plots(self):
        """
        Display the filtered dataset and corresponding plots based on the user's selections.
        """
        # Get the number of users in the filtered dataset
        filtered_length = len(st.session_state.df_selected)
        st.write(f'Cantidad de usuarios: {filtered_length}')  # Display the number of users
        st.write('Data filtrada', st.session_state.df_selected)  # Display the filtered dataset
        
        # Display the appropriate plot based on the selected plot type
        if filtered_length > 0:
            if st.session_state.plot_type == "Exposición a la luz":
                self.FOTICO_luz_natural_8_15_integrada()
                self.FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada()
        else:
            st.write("No data available for the selected filters.")

    def run(self):
        """
        Run the Streamlit app, display the sidebar and data/plots.
        """
        self.display_sidebar()  # Display the sidebar with filters
        self.display_data_and_plots()  # Display the filtered data and corresponding plots

if __name__ == "__main__":
    app = StreamlitApp()  #
    app.run()  #


# streamlit run "/Users/tomasmendietarios/Library/Mobile Documents/com~apple~CloudDocs/I.T.B.A/MRI/Main/main.py"

