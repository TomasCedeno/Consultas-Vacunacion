from django.shortcuts import render
import pandas as pd
from sodapy import Socrata
import dateutil

client = Socrata("www.datos.gov.co", None)
results = client.get("prrv-jnta", limit=20000)
df = pd.DataFrame.from_records(results)

columns = ['Fecha de Aplicación', 'Año', 'Código Territorio', 'Territorio', 'Dosis Aplicadas', 'Fecha Corte']
df.columns = columns

df.dropna(inplace=True, how='any')
df['Fecha de Aplicación'] = df['Fecha de Aplicación'].apply(dateutil.parser.parse, yearfirst=True)
df['Año'] = df['Año'].apply(int)
df['Código Territorio'] = df['Código Territorio'].apply(int)
df['Dosis Aplicadas'] = df['Dosis Aplicadas'].apply(int)
df['Fecha Corte'] = df['Fecha Corte'].apply(dateutil.parser.parse, yearfirst=True)

def home(request):

    table = {
        "df": df.head(15).to_html(classes=("table", "table-striped"), justify='left')
    }

    return render(request, 'index.html', context=table)


def query(request):
    applyDate = request.POST['applyDate']
    year = request.POST['year']
    territory = request.POST['territory']
    doseBig = request.POST['doseBig']
    doseLess = request.POST['doseLess']
    cutOffDate = request.POST['cutOffDate']

    query = ""

    if applyDate:
        query += f"`Fecha de Aplicación` == '{applyDate}'"

    if year:
        query += " & " if query else ""
        query += f"Año == {year}"

    if territory:
        query += " & " if query else ""
        query += f"Territorio.str.lower() == '{territory.lower()}'"

    if doseBig:
        query += " & " if query else ""
        query += f"`Dosis Aplicadas` >= {int(doseBig)}"

    if doseLess:
        query += " & " if query else ""
        query += f"`Dosis Aplicadas` <= {int(doseLess)}"
        
    if cutOffDate:
        query += " & " if query else ""
        query += f"`Fecha Corte` == '{cutOffDate}'"

    dfQuery = df.query(query) if query != "" else df.head(15)

    table = {
        "df": dfQuery.to_html(classes=("table", "table-striped"), justify='left')
    }

    return render(request, 'index.html', context=table)


