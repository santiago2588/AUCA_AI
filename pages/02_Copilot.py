from Calculations.Calculations import *
from langchain.llms import OpenAI

openai_api_key = st.text_input('OpenAI API Key')

def generate_response(input_text):
    llm = OpenAI(temperature=0.3, openai_api_key=openai_api_key)
    st.info(llm(input_text))

prompt_opportunities=f'I want you to act as an energy and carbon emissions consultant with wide experience in the industry. The process {process_hotspot_co2}, which include the equipment {equipment_hotspot_co2}, is currently the highest carbon emitter in my plant, due to the use of the fuel {fuel_hotspot_co2}. I want you to identify the most relevant and easy-to-implement improvement opportunities to reduce the CO2 emissions of this process.'
prompt_action_plan=f'I want you to act as an energy and carbon emissions consultant with wide experience in the industry. The process {process_hotspot_co2}, which include the equipment {equipment_hotspot_co2}, is currently the highest carbon emitter in my plant, due to the use of the fuel {fuel_hotspot_co2}. I want you to generate a professional and detailed climate strategy, including Reduction Targets and Indicators.'

if not openai_api_key.startswith('sk-'):
    st.warning('Please enter your OpenAI API key!', icon='⚠')
if openai_api_key.startswith('sk-'):
    tab1, tab2=st.tabs(['Improvement opportunities','Action plan'])
    with tab1:
        generate_response(prompt_opportunities)
    with tab2:
        generate_response(prompt_action_plan)

# Assume 'response' is the response object from the OpenAI API
if generate_response['choices'][0]['finish_reason'] == 'length':
    st.write("The response is incomplete.")
else:
    st.write("The response is complete.")

st.success(""" 
Congratulations, you have reduced your carbon emissions and energy costs and now your plant is more profitable and efficient!

Contact us if you want to access the Pro Plan so that we can model your company, entering your processes, equipment and energy sources, in order to obtain the performance of your plant and optimize your operations.""")