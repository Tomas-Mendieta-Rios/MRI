import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

# Define the Streamlit app class
class StreamlitApp:
    def __init__(self):
        # Initialize an empty DataFrame and call setup and filter initialization functions
        self.df_all = pd.DataFrame()  
        self.setup()  
        self.initialize_filters() 

    def setup(self):
        # Load the datasets from the specified CSV files
        df_before = pd.read_csv('/Users/tomasmendietarios/Library/Mobile Documents/com~apple~CloudDocs/I.T.B.A/MRI/Data/allData_MiRelojInterno_27Marzo2023.csv')
        df_after = pd.read_csv('/Users/tomasmendietarios/Library/Mobile Documents/com~apple~CloudDocs/I.T.B.A/MRI/Data/allData_MiRelojInterno_24Julio2024.csv')

        # Concatenate the two datasets and reset the index
        self.df_all = pd.concat([df_before, df_after], ignore_index=True)
        
        # Convert the 'date_recepcion_data' column to datetime and sort the data by 'user_id' and 'date_recepcion_data'
        self.df_all['date_recepcion_data'] = pd.to_datetime(self.df_all['date_recepcion_data'])
        self.df_all.sort_values(by=['user_id', 'date_recepcion_data'], ascending=[True, True], inplace=True)
        self.df_all.reset_index(drop=True, inplace=True)
        
        # Calculate the difference in days between consecutive entries for the same user
        self.df_all['days_diff'] = self.df_all.groupby('user_id')['date_recepcion_data'].diff().dt.days.fillna(0)

    def initialize_filters(self):
        # Initialize default filter values and store them in Streamlit's session state
        
        # Date range filters
        if 'date_min' not in st.session_state:
            st.session_state.date_min = self.df_all['date_recepcion_data'].min()
        if 'date_max' not in st.session_state:
            st.session_state.date_max = self.df_all['date_recepcion_data'].max()
        
        # Age filter
        if 'age' not in st.session_state:
            st.session_state.age = [self.df_all['age'].min(), self.df_all['age'].max()]
        
        # Gender filter
        if 'selected_gender' not in st.session_state:
            st.session_state.selected_gender = 'All'
        
        # Filtered data for further use
        if 'df_selected' not in st.session_state:
            st.session_state.df_selected = self.df_all
        
        # Recommendations filters
        if 'selected_recomendaciones' not in st.session_state:
            st.session_state.selected_recomendaciones = 'All'
        if 'selected_recomendaciones_rango_min' not in st.session_state:
            st.session_state.selected_recomendaciones_rango_min = 0
        if 'selected_recomendaciones_rango_max' not in st.session_state:
            st.session_state.selected_recomendaciones_rango_max = 30
        
        # Age categorization flag
        if 'categorize_ages' not in st.session_state:
            st.session_state.categorize_ages = False  # Default to not categorize ages


    def apply_filters(self):
        # Start with the unfiltered dataset
        df_filtered = self.df_all
        
        # Filter based on user entries or users selection
        if st.session_state.usuarios_entradas == 'Usuarios':
            df_filtered = df_filtered.drop_duplicates(subset='user_id', keep='last')
        elif st.session_state.usuarios_entradas == 'Entradas':
            df_filtered = self.df_all.copy()

   
        # Apply date filter if not all dates are selected
        if not st.session_state.get('all_dates', True):
            date_min = pd.to_datetime(st.session_state['date_min'])
            date_max = pd.to_datetime(st.session_state['date_max'])
            df_filtered = df_filtered[(df_filtered['date_recepcion_data'] >= date_min) & (df_filtered['date_recepcion_data'] <= date_max)]
        
        # Apply age filter if not all ages are selected
        if not st.session_state.get('all_ages', True):
            age_min, age_max = st.session_state['age']
            df_filtered = df_filtered[(df_filtered['age'] >= age_min) & (df_filtered['age'] <= age_max)]
        
        # Apply gender filter if a specific gender is selected
        if st.session_state.get('selected_gender', 'All') != 'All':
            df_filtered = df_filtered[df_filtered['genero'] == st.session_state['selected_gender']]

        # Apply recommendations filter based on user selections
        if st.session_state.get('selected_recomendaciones', 'All') != 'All':
            days_min = st.session_state['selected_recomendaciones_rango_min']
            days_max = st.session_state['selected_recomendaciones_rango_max']
            rec_filter = st.session_state['selected_recomendaciones']
            
            if rec_filter == 'Si':
                df_filtered = df_filtered[(df_filtered['SEGUISTE_RECOMENDACIONES'] == 'si') & 
                                        (df_filtered['days_diff'] > days_min) & 
                                        (df_filtered['days_diff'] <= days_max)]
            elif rec_filter == 'No':
                df_filtered = df_filtered[(df_filtered['SEGUISTE_RECOMENDACIONES'] == 'no') & 
                                        (df_filtered['days_diff'] > days_min) & 
                                        (df_filtered['days_diff'] <= days_max)]
        
        # Apply age categorization if requested
        if st.session_state.get('categorize_ages', False):
            self.categorize_age(df_filtered)
        else:
            if 'age_category' in df_filtered.columns:
                df_filtered = df_filtered.drop(columns=['age_category'])

        # Save the filtered DataFrame in session state
        st.session_state['df_selected'] = df_filtered

    def display_sidebar(self):
        # Create the sidebar for filter options
        st.sidebar.header('Filter Options')
        
        # Date filter
        st.session_state.all_dates = st.sidebar.checkbox("All Dates", value=True)
        if not st.session_state.all_dates:
            st.session_state.date_min = st.sidebar.date_input("Start Date", value=self.df_all['date_recepcion_data'].min())
            st.session_state.date_max = st.sidebar.date_input("End Date", value=self.df_all['date_recepcion_data'].max())

        # Age filter
        st.session_state.all_ages = st.sidebar.checkbox("All Ages", value=True)
        if not st.session_state.all_ages:
            st.session_state.age = st.sidebar.slider(
                "Age Range", 
                min_value=int(self.df_all['age'].min()), 
                max_value=int(self.df_all['age'].max()), 
                value=(int(self.df_all['age'].min()), int(self.df_all['age'].max()))
            )
        
        # Gender filter
        st.session_state.all_genders = st.sidebar.checkbox("All Genders", value=True)
        if not st.session_state.all_genders:
            st.session_state.selected_gender = st.sidebar.selectbox("Select Gender", options=self.df_all['genero'].unique().tolist())
        else:
            st.session_state.selected_gender = 'All'

        # Recommendations filter
        st.session_state.all_recomendaciones = st.sidebar.checkbox("All Recommendations", value=True)
        if not st.session_state.all_recomendaciones:
            st.session_state.selected_recomendaciones = st.sidebar.selectbox("Seguiste recomendaciones", options=['Si', 'No'])
            st.session_state.selected_recomendaciones_rango_min = st.sidebar.number_input("Min days difference", min_value=0, max_value=100, value=st.session_state.selected_recomendaciones_rango_min)
            st.session_state.selected_recomendaciones_rango_max = st.sidebar.number_input("Max days difference", min_value=0, max_value=100, value=st.session_state.selected_recomendaciones_rango_max)

        # Age categorization options
        st.session_state.categorize_ages = st.sidebar.checkbox("Categorize Ages", value=st.session_state.categorize_ages)
        if st.session_state.categorize_ages:
            st.sidebar.subheader("Define Age Categories")
            st.session_state.age_joven_min = st.sidebar.slider("Min Age for Jóvenes", min_value=0, max_value=100, value=15)
            st.session_state.age_adult_min = st.sidebar.slider("Min Age for Adultos", min_value=0, max_value=100, value=30)
            st.session_state.age_tercera_edad_min = st.sidebar.slider("Min Age for Tercera Edad", min_value=0, max_value=100, value=60)
        
        # Usuarios entradas
        st.session_state.usuarios_entradas = st.sidebar.radio(
            "Choose Option", 
            options=['Entradas', 'Usuarios']
        )
        
        # Plot type selection
        st.session_state.plot_type = st.sidebar.selectbox("Select Plot Type", options=["Exposición a la luz"])

        # Button to apply filters
        if st.sidebar.button("Apply Filters"):
            self.apply_filters()

    def categorize_age(self, df_filtered):
        # Function to categorize age based on user-defined age ranges
        def age_category(age):
            if age < st.session_state.age_adult_min:
                return 'Jóvenes'
            elif age < st.session_state.age_tercera_edad_min:
                return 'Adultos'
            else:
                return 'Tercera Edad'

        df_filtered['age_category'] = df_filtered['age'].apply(age_category)

    def FOTICO_luz_natural_8_15_integrada(self):
        # Plot exposure to natural light
        if 'age_category' not in st.session_state.df_selected.columns and st.session_state.categorize_ages:
            self.categorize_age(st.session_state.df_selected)

        fig = px.histogram(
            st.session_state.df_selected, 
            x='FOTICO_luz_natural_8_15_integrada', 
            color='genero', 
            barmode='stack',
            nbins=3,
            facet_col='age_category' if 'age_category' in st.session_state.df_selected.columns else None,
            category_orders={"age_category": ["Jóvenes", "Adultos", "Tercera Edad"], "FOTICO_luz_natural_8_15_integrada": [0, 1, 2]},
            title='Exposición a la luz natural'
        )

        # Remove unnecessary text from plot annotations
        fig.for_each_annotation(lambda a: a.update(text=a.text.replace("FOTICO_luz_natural_8_15_integrada", "").replace("age_category=", "")))

        # Update plot layout
        fig.update_layout(
            xaxis=dict(tickmode='array', tickvals=[0, 1, 2], ticktext=['0', '1', '2']),
            yaxis_title='Cantidad de usuarios',
            legend_title_text='Género'
        )

        # Display the plot
        st.plotly_chart(fig)
    
    def FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada(self):
        # Plot exposure to artificial light
        if 'age_category' not in st.session_state.df_selected.columns and st.session_state.categorize_ages:
            self.categorize_age(st.session_state.df_selected)

        fig = px.histogram(
            st.session_state.df_selected, 
            x='FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada', 
            color='genero', 
            barmode='stack',
            nbins=2,
            facet_col='age_category' if 'age_category' in st.session_state.df_selected.columns else None,
            category_orders={"age_category": ["Jóvenes", "Adultos", "Tercera Edad"], "FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada": [0, 1]},
            title='Exposición a la luz artificial'
        )

        # Remove unnecessary text from plot annotations
        fig.for_each_annotation(lambda a: a.update(text=a.text.replace("FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada", "").replace("age_category=", "")))

        # Update plot layout
        fig.update_layout(
            xaxis=dict(tickmode='array', tickvals=[0, 1], ticktext=['0', '1']),
            yaxis_title='Cantidad de usuarios',
            legend_title_text='Género'
        )

        # Display the plot
        st.plotly_chart(fig)

    def display_data_and_plots(self):
        # Display filtered data and the selected plot
        filtered_length = len(st.session_state.df_selected)
        st.write(f'Cantidad de usuarios: {filtered_length}')
        st.write('Data filtrada', st.session_state.df_selected)
        
        # Display appropriate plot based on user selection
        if filtered_length > 0:
            if st.session_state.plot_type == "Exposición a la luz":
                self.FOTICO_luz_natural_8_15_integrada()
                self.FOTICO_luz_ambiente_8_15_luzelect_si_no_integrada()
        else:
            st.write("No data available for the selected filters.")
    
    def run(self):
        # Run the app by displaying the sidebar and filtered data/plots
        self.display_sidebar()
        self.display_data_and_plots()

# Run the Streamlit app
if __name__ == "__main__":
    app = StreamlitApp()
    app.run()

# To run the app, use the command:
# streamlit run "/Users/tomasmendietarios/Library/Mobile Documents/com~apple~CloudDocs/I.T.B.A/MRI/Main/main.py"
