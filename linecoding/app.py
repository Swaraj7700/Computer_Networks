from flask import Flask, render_template, request, Response
import numpy as np
import matplotlib.pyplot as plt
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

app = Flask(__name__)

def unipolar_nrz(data):
    return data

def polar_nrz_l(data):
    return [1 if bit == 1 else -1 for bit in data]

def polar_nrz_i(data):
    output = []
    last = 1
    for bit in data:
        if bit == 1:
            last *= -1
        output.append(last)
    return output

def rz(data):
    rz_output = []
    for bit in data:
        if bit == 1:
            rz_output.extend([1, 0])
        else:
            rz_output.extend([-1, 0])
    return rz_output

def manchester(data):
    manchester_output = []
    for bit in data:
        if bit == 1:
            manchester_output.extend([1, -1])
        else:
            manchester_output.extend([-1, 1])
    return manchester_output

def differential_manchester(data):
    output = []
    last = 1
    for bit in data:
        if bit == 1:
            output.extend([-last, last])
        else:
            last *= -1
            output.extend([last, -last])
    return output

def ami(data):
    last = -1
    output = []
    for bit in data:
        if bit == 1:
            last *= -1
            output.append(last)
        else:
            output.append(0)
    return output

def pseudoternary(data):
    last = -1
    output = []
    for bit in data:
        if bit == 0:
            last *= -1
            output.append(last)
        else:
            output.append(0)
    return output

def plot_line_code(data, encoding_function, title):
    encoded_data = encoding_function(data)
    t = np.arange(0, len(encoded_data))
    fig, ax = plt.subplots()
    ax.step(t, encoded_data, where='post')
    ax.set_ylim(-2, 2)
    ax.set_title(title)
    ax.set_xlabel('Time')
    ax.set_ylabel('Amplitude')
    ax.grid(True)
    return fig

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_data = request.form['data']
        try:
            data = [int(bit) for bit in input_data]
            figures = []

            figures.append(plot_line_code(data, unipolar_nrz, 'Unipolar NRZ'))
            figures.append(plot_line_code(data, polar_nrz_l, 'Polar NRZ-L'))
            figures.append(plot_line_code(data, polar_nrz_i, 'Polar NRZ-I'))
            figures.append(plot_line_code(data, rz, 'RZ'))
            figures.append(plot_line_code(data, manchester, 'Manchester'))
            figures.append(plot_line_code(data, differential_manchester, 'Differential Manchester'))
            figures.append(plot_line_code(data, ami, 'AMI'))
            figures.append(plot_line_code(data, pseudoternary, 'Pseudoternary'))

            output = io.BytesIO()
            fig, axes = plt.subplots(len(figures), 1, figsize=(10, 20))
            for ax, figure in zip(axes, figures):
                canvas = FigureCanvas(figure)
                figure.tight_layout()
                canvas.draw()
                buf = canvas.buffer_rgba()
                image = np.asarray(buf)
                ax.imshow(image)
                ax.axis('off')
            
            fig.tight_layout()
            FigureCanvas(fig).print_png(output)
            return Response(output.getvalue(), mimetype='image/png')
        except ValueError:
            return "Invalid input. Please enter a string of 0s and 1s."

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
