from flask import Flask, render_template, request
import plotly
import plotly.graph_objs as go
import json
import xlrd


class Record:
    def __init__(self, name):
        self.name = name
        self.measurements = []

    def add_measurement(self, measurement):
        self.measurements.append(measurement)

    def to_dict(self):
        return {self.name: self.measurements}


def getPatientsList(path):
    valuesList = []
    valuesList.append('Choose a patient')
    wb = xlrd.open_workbook(path)
    sheet = wb.sheet_by_index(0)
    for i in range(1, sheet.nrows):
        item = sheet.cell_value(i, 0)
        if item not in valuesList:
            valuesList.append(item)
    valuesList.sort()
    return valuesList


def getArrayData(path, id):
    valuesList = []
    wb = xlrd.open_workbook(path)
    sheet = wb.sheet_by_index(0)
    for i in range(1, sheet.ncols):
        valuesList.append(Record(sheet.cell_value(0, i)))

    for i in range(sheet.nrows):
        pid = sheet.cell_value(i, 0)
        if pid == id:
            for j in range(1, sheet.ncols):
                valuesList[j - 1].add_measurement(sheet.cell_value(i, j))

    return valuesList


def getLayout(minval, maxval):
    layout = go.Layout(
        yaxis=dict(
            title='Patient cardiological measurements',
            zeroline=True,
            #range=[minval, maxval]
        ),
        boxmode='group')
    return layout

path = "c:\\Dev\\patient_values2.xlsx"
app = Flask(__name__)

@app.route('/')
def hello_method():


    patientslist = getPatientsList(path)

    trace = go.Box(y=[], name='', boxpoints='outliers')
    pdata = [trace]
    data = pdata
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    selectedpatient = 'Choose patient'

    return render_template('capp.html', patients=patientslist, graphJSON=graphJSON, selectedpatient=selectedpatient)


@app.route('/plot', methods=['GET', 'POST'])
def plot():
    #path = "c:\\Dev\\patient_values2.xlsx"

    pid = request.form['patients']

    pdata=[]
    patientslist = getPatientsList(path)

    valuesList = getArrayData(path, pid)

    for i in range(0, len(valuesList)):
        rec = valuesList[i]
        trace = go.Box(y=rec.measurements, name=rec.name, boxpoints='outliers')
        pdata.append(trace)

    graphJSON = json.dumps(pdata, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('capp.html', patients=patientslist, graphJSON=graphJSON, selectedpatient=pid)


if __name__ == '__main__':
    app.run()
