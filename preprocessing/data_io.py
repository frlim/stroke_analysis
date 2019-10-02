from pathlib import Path
import xlwings as xw
import pandas as pd
import download

# DTN_PATH = Path('Z:\\stroke_data')
_stroke_dir = Path('Z:\\stroke_data\\')
RAW_DATA = _stroke_dir / 'raw_data'
PROCESSED_DATA = _stroke_dir / 'processed_data'
output = _stroke_dir / 'scratch_output'


def DTN(dtn_file=PROCESSED_DATA / 'deidentified_DTN.xlsx',cell_range='A1:M275'):
    return xw.Book(str(dtn_file)).sheets[0].range(cell_range).options(
        convert=pd.DataFrame, index=False, header=True).value


def HOSP_KEY(key_file=PROCESSED_DATA / 'hospital_keys.xlsx',cell_range='A1:C275'):
    return xw.Book(str(key_file)).sheets[0].range(cell_range).options(
        convert=pd.DataFrame, index=False, header=True).value


def HOSP_ADDY(addy_file=RAW_DATA / 'AHA 2012 ID codes.xlsx'):
    return pd.read_excel(
        addy_file,
        header=None,
        names=['AHA_ID', 'Name', 'Street', 'City', 'ZIP', 'State'])


def cleaned_KORI_GRANT(kori_grant=RAW_DATA / 'KORI_GRANT.xlsx'):
    cell_range = 'A27:AD311'
    return xw.Book(str(kori_grant)).sheets[0].range(cell_range).options(
        convert=pd.DataFrame, index=False,
        header=True).value.drop_duplicates()

def JC_StrokeCetification(path=RAW_DATA / 'StrokeCertificationList.xlsx'):
    JC_URL = "https://www.qualitycheck.org/file.aspx?FolderName=" + "StrokeCertification&c=1"
    if not path.exists():
        download.download_file(JC_URL, 'Joint Commission', savedir=path)
    return pd.read_excel(path,dtype=str)
