from pathlib import Path
import os

# if os.name == 'nt':
#     DTN_PATH = Path('Z:\\stroke_data\\processed_data')
#     MODELOUT_PATH = Path.cwd().parent / 'patrick_stroke' / 'output'
#     LOCAL_OUTPUT = Path('F:\\stroke_model_output\\output_111419')
#     MARKOV_ANALYSIS_OUTPUT = Path(
#         'F:\\stroke_model_output\\markov_describe_111419\\')
#     BASIC_ANALYSIS_OUTPUT = Path(
#         'F:\\stroke_model_output\\results_analysis_111419\\')
#     GRAPH_OUTPUT = Path('F:\\stroke_model_output\\plots_111419\\')
# else:
#     DTN_PATH = Path('~/deidentified_stroke_data')
#     MODELOUT_PATH = Path.cwd().parent / 'patrick_stroke' / 'output'
#     LOCAL_OUTPUT = Path('/sda1/stroke_model_output/output_080619')
#     MARKOV_ANALYSIS_OUTPUT = Path(
#         '/sda1/stroke_model_output/markov_describe_080619')
#     BASIC_ANALYSIS_OUTPUT = Path(
#         '/sda1/stroke_model_output/results_analysis_080619')
#     GRAPH_OUTPUT = Path('/sda1/stroke_model_output/plots_080619')

# _stroke_dir = Path('/Volumes/DOM_DGM_HUR$/stroke_data')
_stroke_dir = Path('/Users/Ryan/Stroke_scripts')
DTN_PATH  = _stroke_dir / 'processed_data'
HOSPITAL_ADDY = DTN_PATH / 'hospital_address_NE_for_stroke_locations.csv'
HOSP_KEY_PATH = DTN_PATH /'hospital_keys_master_v2.csv'

OUTPUT = _stroke_dir/'stroke_model_output'
GRAPH_OUTPUT = OUTPUT/'maps'
LOCAL_OUTPUT = OUTPUT/'output_072820'
BASIC_ANALYSIS_OUTPUT = OUTPUT/'analyzed_output_072820'
