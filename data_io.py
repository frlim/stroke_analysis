from pathlib import Path
import os

if os.name == 'nt':
    DTN_PATH = Path('Z:\\stroke_data\\processed_data')
    MODELOUT_PATH = Path.cwd().parent / 'patrick_stroke' / 'output'
    LOCAL_OUTPUT = Path('F:\\stroke_model_output\\output_080619')
    MARKOV_ANALYSIS_OUTPUT = Path(
        'F:\\stroke_model_output\\markov_describe_080619\\')
    BASIC_ANALYSIS_OUTPUT = Path(
        'F:\\stroke_model_output\\results_analysis_080619\\')
    GRAPH_OUTPUT = Path('F:\\stroke_model_output\\plots_080619\\')
else:
    DTN_PATH = Path('~/deidentified_stroke_data')
    MODELOUT_PATH = Path.cwd().parent / 'patrick_stroke' / 'output'
    LOCAL_OUTPUT = Path('/sda1/stroke_model_output/output_080619')
    MARKOV_ANALYSIS_OUTPUT = Path(
        '/sda1/stroke_model_output/markov_describe_080619')
    BASIC_ANALYSIS_OUTPUT = Path(
        '/sda1/stroke_model_output/results_analysis_080619')
    GRAPH_OUTPUT = Path('/sda1/stroke_model_output/plots_080619')
