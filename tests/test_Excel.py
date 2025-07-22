import pandas as pd
import tempfile
from src.getFolders import save_to_excel

def test_save_to_excel_creates_file(tmp_path):
    data = [{"Name":"n","Path":"p","Parent":"pr","Depth":0}]
    out = tmp_path / "out.xlsx"
    save_to_excel(data, str(out))
    # read back and verify
    df = pd.read_excel(str(out))
    assert list(df.columns) == ["Name","Path","Parent","Depth"]
    assert df.iloc[0]["Name"] == "n"