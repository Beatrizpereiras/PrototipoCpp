from css_demod import demodule_wav
from css_demod import plot_wav
import matplotlib.pyplot as plt
import numpy as np
import os
from PIL import ImageTk
from PIL import Image as PilImage
import pyaudio
from scipy.io import wavfile
from tkinter import *
from tkinter import filedialog


# Frequência Mínima padrão
default_min_freq = 1000
# Frequência Máxima padrão
default_max_freq = 2000
# Duração Padrão
default_duration = 1.0
# Taxa de Amostragem
sample_rate = 48000

plt.rcParams.update({'font.size': 18})

# Função que gera o tom
def generate_tone(bit_number, duration_seconds):
    min_freq = float(entry_min_freq.get())
    max_freq = float(entry_max_freq.get())
    base_freq = min_freq + (bit_number / 16) * (max_freq-min_freq)
    time = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds))
    frequency_array = np.linspace(base_freq, base_freq + (max_freq-min_freq), len(time))

    # For que gera o comportamento característico do chirp
    for i in range(len(frequency_array)):
        while frequency_array[i] > max_freq:
            frequency_array[i] -= (max_freq-min_freq)

    tone = np.sin(2 * np.pi * frequency_array * time)

    return tone, time, frequency_array

#Função que gera um tom crescente, da frequência mínima para a máxima
def generate_increasing_tone(duration_seconds):
    min_freq = float(entry_min_freq.get())
    max_freq = float(entry_max_freq.get())
    start_freq = min_freq
    end_freq = max_freq
    time = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds/2))
    frequency_array = np.linspace(start_freq, end_freq, len(time))
    tone = np.sin(2 * np.pi * frequency_array * time)
    return tone, time, frequency_array

#Função que gera um tom decrescente, da frequência máxima para a mínima
def generate_decreasing_tone(duration_seconds):
    min_freq = float(entry_min_freq.get())
    max_freq = float(entry_max_freq.get())
    start_freq = max_freq
    end_freq = min_freq
    time = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds/2))
    frequency_array = np.linspace(start_freq, end_freq, len(time))
    tone = np.sin(2 * np.pi * frequency_array * time)
    return tone, time, frequency_array

#Função que toca o tom
def play_tone(bit_number, duration_seconds):
    tone, _, _ = generate_tone(bit_number, duration_seconds)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=sample_rate, output=True)
    stream.write(tone.astype(np.float32).tobytes())
    stream.stop_stream()
    stream.close()
    p.terminate()


# Função que plota a variação da frequência no tempo referente ao byte
def plot_frequency_time(bit_number1, bit_number2, duration_seconds):
    tone1, time1, frequency_array1 = generate_tone(bit_number1, duration_seconds / 2)
    tone2, time2, frequency_array2 = generate_tone(bit_number2, duration_seconds / 2)
    plt.figure(figsize=(10, 8))
    plt.scatter(time1, frequency_array1, s=1, c='b', marker='.')
    plt.scatter(time2 + duration_seconds / 2, frequency_array2, s=1, c='r', marker='.')
    plt.title('Padrão do Código de Espalhamento')
    plt.xlabel('Tempo')
    plt.ylabel('Frequência')
    plt.grid()
    plt.show()

# Função que plota a variação da frequência no tempo referente ao texto
def plot_frequency_time_text(text, duration_seconds):
    binary_text = ' '.join(format(ord(i), '08b') for i in text)
    binary_list = binary_text.split(' ')
    total_duration = len(binary_list) * duration_seconds + 2.5  # Updated total duration
    time = np.linspace(0, total_duration, int((sample_rate) * (total_duration)))
    print(len(time))
    frequencies = []

    # Add three increasing chirps at the beginning
    _, _,sync_tone = generate_increasing_tone(duration_seconds)
    sync_tone_twice = np.concatenate((sync_tone, sync_tone))
    sync_tone_thrice = np.concatenate((sync_tone_twice, sync_tone))
    frequencies.extend(sync_tone_thrice)
    print(len(frequencies))
    current_time = (duration_seconds/2) * 3  # Move the current time after the three chirps

    # Loop through the binary list and add frequency data
    for binary_num in binary_list:
        bit_number = int(binary_num, 2)
        first_half = bit_number >> 4
        second_half = bit_number & 0b1111
        tone_duration = duration_seconds/2
        _, _, frequency_array1 = generate_tone(first_half, tone_duration)
        _, _, frequency_array2 = generate_tone(second_half, tone_duration)
        frequencies.extend(frequency_array1)
        print(len(frequencies))

        frequencies.extend(frequency_array2)
        print(len(frequencies))

        current_time += duration_seconds

    # Add two decreasing chirps at the end
    _, _, end_tone = generate_decreasing_tone(duration_seconds)
    end_tone_twice = np.concatenate((end_tone, end_tone))
    frequencies.extend(end_tone_twice)
    print(len(frequencies))
    # Plot the scatter graph
    plt.figure(figsize=(10, 8))
    plt.scatter(time, frequencies, s=0.5, c='b')
    plt.title('Chirps corresponding to the Modulated Text')
    plt.xlabel('Time')
    plt.ylabel('Frequency')
    plt.grid()
    plt.show()


# Função que recebe o byte e toca o som
def get_input():
    bit_number = int(entry.get(), 2)
    duration_seconds = float(entry_duration.get())
    first_half = bit_number & 0b1111
    second_half = (bit_number >> 4) & 0b1111
    play_tone(first_half, duration_seconds / 2)
    play_tone(second_half, duration_seconds / 2)


# Função que toca os sons referentes ao texto
def convert_and_play_text(output_filename="output.wav"):
    text = entry_text.get()
    duration_seconds = float(entry_duration.get())

    # Tocando os Sync Chirps
    sync_tone, _, _ = generate_increasing_tone(duration_seconds)
    sync_tone_twice = np.concatenate((sync_tone, sync_tone))
    sync_tone_thrice= np.concatenate((sync_tone_twice, sync_tone))
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=sample_rate, output=True)
    stream.write(sync_tone_thrice.astype(np.float32).tobytes())
    stream.stop_stream()
    stream.close()

    # Tocando os dois chirps de cada caracter
    for char in text:
        first_half = (ord(char) >> 4) & 0b1111
        second_half = ord(char) & 0b1111
        play_tone(first_half, duration_seconds / 2)
        play_tone(second_half, duration_seconds/2)

    # Tocando os End Chirps
    end_tone, _, _ = generate_decreasing_tone(duration_seconds)
    end_tone_twice = np.concatenate((end_tone, end_tone))
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=sample_rate, output=True)
    stream.write(end_tone_twice.astype(np.float32).tobytes())
    stream.stop_stream()
    stream.close()

#Função para gerar o arquivo .wav referente ao texto digitado na GUI
def generate_wav():
    output_folder = "wav_files"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_filename = os.path.join(output_folder, entry_filename.get() + ".wav")
    text = entry_text.get()
    duration_seconds = float(entry_duration.get())
    tones = []
    sync_tone, _, _ = generate_increasing_tone(duration_seconds)
    sync_tone_twice = np.concatenate((sync_tone, sync_tone))
    sync_tone_thrice = np.concatenate((sync_tone_twice, sync_tone))
    tones.append(sync_tone_thrice)
    for char in text:
        first_half = (ord(char) >> 4) & 0b1111
        second_half = ord(char) & 0b1111
        tone1, _, _ = generate_tone(first_half, duration_seconds/2)
        tone2, _, _ = generate_tone(second_half, duration_seconds/2)
        tones.append(tone1)
        tones.append(tone2)

    # Add the ending decreasing tone played twice
    end_tone, _, _ = generate_decreasing_tone(duration_seconds)
    end_tone_twice = np.concatenate((end_tone, end_tone))
    tones.append(end_tone_twice)

    # Concatenate all the tones into a single array
    concatenated_tones = np.concatenate(tones)

    # Convert the list to a numpy array
    tones_np = np.array(concatenated_tones)

    # Save the tones to a .wav file
    wavfile.write(output_filename, 48000, tones_np.astype(np.float32))

#Função intermediária para que o botão chame a função de plot do byte com os devidos argumentos
def plot_freq_time():
    bit_number = int(entry.get(), 2)
    duration_seconds = float(entry_duration.get())
    first_half = bit_number & 0b1111
    second_half = (bit_number >> 4) & 0b1111

    plot_frequency_time(second_half,first_half, duration_seconds)

#Função intermediária para que o botão chame a função de plot do texto com os devidos argumentos
def plot_freq_time_text():
    text = entry_text.get()
    duration_seconds = float(entry_duration.get())
    plot_frequency_time_text(text, duration_seconds)


# Variável global para armazenar o nome do arquivo selecionado

selected_file = ""
# Função para selecionar qual arquivo .wav deseja demodular
def select_file():
    global selected_file
    initial_dir = "./wav_files"
    file_path = filedialog.askopenfilename(initialdir=initial_dir, filetypes=[("WAV files", "*.wav")])
    selected_file = file_path
    demodulated_text = demodule_wav(file_path)  # Assuming demodule_wav now accepts the file path as an argument

    # Create a new pop-up window
    new_window = Toplevel(root)
    new_window.title("Texto Demodulado")
    new_window.geometry("500x100")

    demod_label_new = Label(new_window, text=demodulated_text, font=('Arial', 16, 'bold'))
    demod_label_new.pack(pady=20)
def plot_selected_file():
    if selected_file:
        plot_wav(selected_file)
    else:
        print("Nenhum arquivo selecionado.")

# Criando a interface de usuário
root = Tk()
root.title("Modulador CSS")

# Get the screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set the size of the window to the size of the monitor
root.geometry(f"{screen_width}x{screen_height}")

root.configure()
title_label = Label(root, text="", font=('Arial', 20, 'bold'))
title_label.pack(pady=10)

title_label2 = Label(root, text="Modulador de Sinais em CSS", font=('Arial', 20, 'bold'))
title_label2.pack(pady=10)

label_min_freq = Label(root, text="Insira as Frequências:")
label_min_freq.pack(pady=2)

freq_frame = Frame(root)
freq_frame.pack()

label_min = Label(freq_frame, text="Min:")
label_min.pack(side='left', padx=5, pady=2)

entry_min_freq = Entry(freq_frame, width=5, font=('arial', 12))
entry_min_freq.pack(side='left', padx=10, pady=2)

label_min = Label(freq_frame, text="Max:")
label_min.pack(side='left', padx=10, pady=2)

entry_max_freq = Entry(freq_frame, width=5, font=('arial', 12))
entry_max_freq.pack(side='left', padx=5, pady=2)

label_duration = Label(root, text="Insira a Duração (em segundos):")
label_duration.pack(pady=4)

entry_duration = Entry(root, width=5, font=('arial', 12))
entry_duration.pack(pady=2)

label = Label(root, text="Insira um Valor em 8-Bits:")
label.pack(pady=4)

input_frame = Frame(root)
input_frame.pack(pady=2)

entry = Entry(input_frame, width=60, font=('arial', 12))
entry.pack(side='left')

button_tone = Button(input_frame, text="Play", command=get_input)
button_tone.pack(side='left', padx=5)

label_text = Label(root, text="Insira Seus Dados em Forma de Texto:")
label_text.pack(pady=4)

text_frame = Frame(root)
text_frame.pack()

entry_text = Entry(text_frame, width=60, font=('arial', 12))
entry_text.pack(side='left', pady=2)

button_text = Button(text_frame, text="Play", command=convert_and_play_text)
button_text.pack(side='left', padx=5)

label_filename = Label(root, text="Insira o Nome do Arquivo que Deseja Gerar: ")
label_filename.pack(pady=4)

entry_filename = Entry(root, width=20, font=('arial', 12))
entry_filename.pack(pady=4)

button_generate_wav = Button(root, text="Gerar Arquivo .wav", command = generate_wav, width=20)
button_generate_wav.pack(pady=6)

separation_label2 = Label(root, text="Gráficos da Modulação", font=('Arial', 14, 'bold'))
separation_label2.pack(pady=4)

button_freq_time = Button(root, text="Gráfico 8-Bits", command=plot_freq_time, width=20)
button_freq_time.pack()

button_freq_time_text = Button(root, text="Gráfico Texto", command=plot_freq_time_text, width=20)
button_freq_time_text.pack(pady=4)


separation_label3 = Label(root, text="Demodulação", font=('Arial', 14, 'bold'))
separation_label3.pack(pady=4)


button_select_file = Button(root, text="Demodulação do .wav", command=select_file, width=20)
button_select_file.pack()

button_plot_wav = Button(root, text="Gráfico Demodulação", command=plot_selected_file, width=20)
button_plot_wav.pack(pady=4)


entry_min_freq.insert(0, str(default_min_freq).center(5))
entry_max_freq.insert(0, str(default_max_freq).center(5))
entry_duration.insert(0, str(default_duration).center(5))

image_path1 = "logo-unifei.png"  # Replace with the actual path to your image

img1 = PilImage.open(image_path1)

# Resize the image if necessary
img1 = img1.resize((screen_width // 5, screen_height // 7))  # Ajuste o tamanho conforme necessário
# Convert the image for Tkinter
photo1 = ImageTk.PhotoImage(img1)

# Create a label to display the image
image_label1 = Label(root, image=photo1)
image_label1.image = photo1  # Keep a reference
image_label1.pack(side=LEFT, anchor=SW, padx=10, pady=10)  # Adjust the padding as needed


image_path2 = "logo-iesti.png"  # Replace with the actual path to your image

img2 = PilImage.open(image_path2)

# Resize the image if necessary
img2 = img2.resize((screen_width // 5, screen_height // 7))  # Ajuste o tamanho conforme necessário
# Convert the image for Tkinter
photo2 = ImageTk.PhotoImage(img2)

# Create a label to display the image
image_label2 = Label(root, image=photo2)
image_label2.image = photo2  # Keep a reference
image_label2.pack(side=RIGHT, anchor=SW, padx=10, pady=10)  # Adjust the padding as needed


label_min_freq.configure( font=('Arial', 12))
label_duration.configure(font=('Arial', 12))
label.configure( font=('Arial', 12))
label_text.configure( font=('Arial', 12))
label_filename.configure( font=('Arial', 12))
button_generate_wav.configure( font=('Arial', 12))
button_tone.configure(background='lightblue', font=('Arial', 12))
button_freq_time.configure(background='lightblue', font=('Arial', 12))
button_text.configure(background='lightblue', font=('Arial', 12))
button_freq_time_text.configure(background='lightblue', font=('Arial', 12))
button_select_file.configure(background='lightgrey', font=('Arial', 12))
button_generate_wav.configure(background='lightgrey', font=('Arial', 12))
button_plot_wav.configure(background='lightblue', font=('Arial', 12))




root.mainloop()