from flask import Flask, render_template, flash, request, url_for, redirect
import pandas as pd
import numpy as np
import ast
from dbconnect import connection
import json
import plotly
import chart_studio.plotly as py
import plotly.graph_objs as go
app = Flask(__name__)
app.secret_key = "super secret key"
def AngleofRepose_Points(AngleofRepose, table):
    try:
        AngleofRepose = round(ast.literal_eval(AngleofRepose))
        if AngleofRepose >= 25 and AngleofRepose <= 90:
            idx = table.index[table['Angle of repose'] == AngleofRepose].tolist()[0]
            return table['Angle of repose points'][idx]
        elif AngleofRepose >= 0 and AngleofRepose < 25:
            return 25
        else:
            flash("Invalid Angle of Repose Value")
    except TypeError:
        flash("Invalid Angle of Repose Value")

def Compressibility_Points(Compressibility, table):
    try:
        Compressibility = round(ast.literal_eval(Compressibility))
        if Compressibility >= 5 and Compressibility <= 45:
            idx = table.index[table['Compressibility'] == Compressibility].tolist()[0]
            return table['Compressibility points'][idx]
        elif Compressibility >= 0 and Compressibility < 5:
            return 25
        elif Compressibility > 45:
            return 0
        else:
            flash("Invalid Compressibility Value")
    except TypeError:
        flash("Invalid Compressibility Value")

def AngleofSpatula_Points(AngleofSpatula, table):
    try:
        AngleofSpatula = round(ast.literal_eval(AngleofSpatula))
        if AngleofSpatula >= 25 and AngleofSpatula <= 99:
            idx = table.index[table['Angle of spatula'] == AngleofSpatula].tolist()[0]
            return table['Angle of spatula points'][idx]
        elif AngleofSpatula >= 0 and AngleofSpatula < 25:
            return 25
        elif AngleofSpatula > 99:
            return 0
        else:
            flash("Invalid Angle of Spatula Value")
    except TypeError:
        flash("Invalid Angle of Spatula Value")

def UniformityCoeff_Points(UniformityCoeff, table):
    try:
        UniformityCoeff = round(ast.literal_eval(UniformityCoeff))
        if UniformityCoeff >= 1 and UniformityCoeff <= 36:
            idx = table.index[table['Uniformity coefficient'] == UniformityCoeff].tolist()[0]
            return table['Uniformity coefficient points'][idx]
        elif UniformityCoeff > 0 and UniformityCoeff < 1:
            return 25
        elif UniformityCoeff == 0 or UniformityCoeff > 36:
            return 0
        else:
            flash("Invalid Uniformity Coefficient Value")
    except TypeError:
        flash("Invalid Uniformity Coefficient Value")

def Cohesion_Points(Cohesion, table):
    try:
        Cohesion = round(ast.literal_eval(Cohesion))
        if Cohesion >= 6 and Cohesion <= 79:
            idx = table.index[table['Cohesion'] == Cohesion].tolist()[0]
            return table['Cohesion points'][idx]
        elif Cohesion > 0 and Cohesion < 6:
            return 15
        elif Cohesion == 0 or Cohesion > 79:
            return 0
        else:
            flash("Invalid Cohesion Value")
    except TypeError:
        flash("Invalid Cohesion Value")

def Determine_Flowability(FlowabilityPoints, table):
    FlowabilityPoints = round(FlowabilityPoints)
    if FlowabilityPoints >= 0 and FlowabilityPoints <= 100:
        idx = table.index[table['Flowability points'] == FlowabilityPoints].tolist()[0]
        return table['Flowability'][idx]
    else:
        flash("Invalid Flowability point")

@app.route('/', methods=['GET','POST'])
def index():
    c, conn = connection()
    c.execute("SELECT * FROM materials;")
    all_materials = c.fetchall()

    if request.method == "POST":
        if request.form['btn'] == 'Submit':            
            MaterialName = request.form['MaterialName']
                    
            c.execute("SELECT * FROM materials WHERE MaterialName=?", (MaterialName,))
            x = c.fetchone()
            if x is not None:
                flash("That material name was already in use, please choose another one")
                return redirect(url_for('index'))
            
            else:
                AngleofRepose = request.form['AngleofRepose']
                Compressibility = request.form['Compressibility']
                AngleofSpatula = request.form['AngleofSpatula']
                UniformityCoeff = request.form['UniformityCoeff']
                Cohesion = request.form['Cohesion']
            
                # Read in flowability table
                FlowabilityTable = pd.read_csv("flowability_table.csv")
                
                # Calculate points
                AngleofReposePoints = AngleofRepose_Points(AngleofRepose, FlowabilityTable)
                CompressibilityPoints = Compressibility_Points(Compressibility, FlowabilityTable)
                AngleofSpatulaPoints = AngleofSpatula_Points(AngleofSpatula, FlowabilityTable)
                UniformityCoeffPoints = UniformityCoeff_Points(UniformityCoeff, FlowabilityTable)
                CohesionPoints = Cohesion_Points(Cohesion, FlowabilityTable)
                FlowabilityPoints = AngleofReposePoints + CompressibilityPoints + AngleofSpatulaPoints + UniformityCoeffPoints + CohesionPoints
                Flowability = Determine_Flowability(FlowabilityPoints, FlowabilityTable)

                # Store data in the database
                insert_material = (MaterialName, AngleofRepose, Compressibility, AngleofSpatula, UniformityCoeff, Cohesion, FlowabilityPoints, Flowability)
                c.execute("INSERT INTO materials VALUES (?, ?, ?, ?, ?, ?, ?, ?)", insert_material)
                conn.commit()
                conn.close()
                return redirect(url_for('index'))

        if 'Delete' in request.form['btn']:
            MaterialName = request.form['btn'][7:]
            c.execute("DELETE FROM materials WHERE MaterialName=?", (MaterialName,))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        
        if 'Plot' in request.form['btn']:
            MaterialNames = request.form.getlist('checkbox')
            
            if len(MaterialNames) == 0:
                flash("Please Select Materials")
                return redirect(url_for('index'))
            
            data = []
            for name in MaterialNames:
                c.execute("SELECT * FROM materials WHERE MaterialName=?", (name,))
                x = c.fetchone()

                # Read in flowability table
                FlowabilityTable = pd.read_csv("flowability_table.csv")
                AngleofReposePoints = AngleofRepose_Points(x[1], FlowabilityTable)
                CompressibilityPoints = Compressibility_Points(x[2], FlowabilityTable)
                AngleofSpatulaPoints = AngleofSpatula_Points(x[3], FlowabilityTable)
                UniformityCoeffPoints = UniformityCoeff_Points(x[4], FlowabilityTable)
                CohesionPoints = Cohesion_Points(x[5], FlowabilityTable)
            
                # Create a trace
                trace = go.Scatterpolar(
                    r = [AngleofReposePoints, CompressibilityPoints, AngleofSpatulaPoints, UniformityCoeffPoints, CohesionPoints, AngleofReposePoints],
                    theta = ['Angle of Repose Points','Compressibility Points','Angle of Spatula Points', 'Uniformity Coefficient Points', 'Cohesion Points', 'Angle of Repose Points'],
                    fill = 'toself',
                    name = name
                )
                data.append(trace)

            layout = go.Layout(
                polar = dict(
                    radialaxis = dict(
                    visible = True,
                    range = [0, 25],
                    showgrid = False,
                    )
                ),
                showlegend = True,
            )

            fig = dict(data=data, layout=layout)

            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

            return render_template('index.html',all_materials=all_materials, graphJSON=graphJSON)

    return render_template("index.html", all_materials=all_materials)

if __name__=='__main__':
    app.run(debug=True, port=3134)
