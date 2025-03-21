import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.signal as signal
import scipy.io.wavfile as wav



def demodule_wav(filename):
    sample_rate, data = wav.read(filename)

    # Calcula a transformada de Hilbert do sinal
    data_hilbert = signal.hilbert(data)
    duration=len(data)/sample_rate
    #print(duration)

    segment_size = 24000  # Tamanho do segmento

    # Faz o array que irá armazenar os resultados da transformada de Hilbert para cada segmento a fim de evitar o bug após o 18o caracter
    data_hilbert_array = np.zeros_like(data, dtype=np.complex128)
    for i in range(0, len(data), segment_size):
        segment = data[i:i + segment_size]
        data_hilbert_segment = signal.hilbert(segment)
        data_hilbert_array[i:i + segment_size] = data_hilbert_segment
    values = []
    instants = []

    # Força valores de 0.5 em 0.5 afim de mitigar problemas em relação ao código não pegar o fim de um chirp
    step = 0.5
    start_time = 1.5
    end_time = duration - 0.99

    for i in np.arange(start_time, end_time, step):
        values.append("{:.5f}".format(i))

    for i in np.arange(start_time, end_time, step):
        instants.append("{:.5f}".format(i))


    # Calcular as quebras de fase a partir da fase do sinal analítico
    phase = np.unwrap(np.angle(data_hilbert_array))
    phase_break = (np.diff(phase) / (2.0 * np.pi) * sample_rate)
    #Guardando o tempo em segundos de cada quebra de fase
    # que ocorreu após os Sync Chirps e antes dos End Chirps
    frequencies=[]
    last_frequency=phase_break[0]
    for i in range(0, (len(phase_break) - 1)):
        if phase_break[i] - last_frequency < -350:
            moment = i / sample_rate

            if 1.5 <= moment <= (duration - 1):
                instants.append("{:.5f}".format(moment))
                frequencies.append("{:.5f}".format(phase_break[i]))
        last_frequency = phase_break[i]

    #É necessário reordenar a lista para que os momentos da quebra de fase e os pontos forçados no começo do código fiquem em ordem crescente
    instants_float = [float(i) for i in instants]
    ordered_instants = sorted(instants_float)
    precision = 5
    ordered_instants_string = [f"{value:.{precision}f}" for value in ordered_instants]

    #print("Lista ordenada:", ordered_instants_str)

    #print(len(ordered_instants_str))


   # Eliminar duplicatas. Na quebra de fase dois momentos muito próximos podedm ser pegos e também é necessário eliminar cópias dos finais de cada chirp
    instants_no_duplicates = [ordered_instants_string[0]]
    for value in ordered_instants_string[1:]:
        if not any(np.isclose(float(value), float(v), atol=0.00500) for v in instants_no_duplicates):
            instants_no_duplicates.append(value)

    #print(instants_no_duplicates)

    # É realizada a subtração de cada termo com o seguinte para identificar a duração da rampa de cada chirp
    ramp_time = []
    for i in range(1, len(instants_no_duplicates)):
        diff = "{:.5f}".format(float(instants_no_duplicates[i]) - float(instants_no_duplicates[i - 1]))
        ramp_time.append(diff)

    #print(f'Subtração entre pares de tempo: {ramp_time}')

    # Com a duração de rampa de cada chirp é necessário então pegar apenas o primeiro valor de cada caso em que a soma entre ele e o próximo seja próxima de 0.5, com uma exceção para os valores iguais a 0.5
    desired_ramp_time = []
    counter = 0
    for i in range(len(ramp_time)):
        current_diff = float(ramp_time[i])
        if np.isclose(current_diff, 0.500, atol=0.001):  # Checking if the element is close to 0.500
            desired_ramp_time.append(current_diff)
            counter += 1
            if counter % 2 != 0:  # Make sure the counter is even
                counter += 1
        else:
            if counter % 2 ==0:
                # Checking the sum of the current element and the next element
                sum_current_next = current_diff + float(ramp_time[i + 1]) if i + 1 < len(ramp_time) else current_diff
                if np.isclose(sum_current_next, 0.500, atol=0.001):  # Checking if the sum is close to 0.500
                    desired_ramp_time.append(current_diff)
                    counter += 1
            else:
                counter+=1


    #print(elementos_uteis)
    
    
    desired_ramp_time_str = [f"{value:.{precision}f}" for value in desired_ramp_time]
    #print(elementos_uteis_str)
    
    excel_data = pd.read_excel(
        'nibble_ascii.xlsx')  

    
    desired_ramp_time_float = [float(value[:-2]) for value in desired_ramp_time_str]
    #print(desired_ramp_time_float)

    tolerance = 0.005  # Tolerância de proximidade desejada

    # Retorna os valores de frequência correspondentes aos tempos de rampa.
    corresponding_frequencies = [
        excel_data.loc[np.isclose(excel_data['Tempo'], value, atol=tolerance), 'Hertz'].values[0]
        for value in desired_ramp_time_float
    ]

    #print(corresponding_frequencies)


    # Agrupa as frequências correspondentes em pares pois cada letra utiliza dois nibbles e busca a letra correspondente para cada par de nibble
    pairs = [(corresponding_frequencies[i], corresponding_frequencies[i + 1]) for i in range(0, len(corresponding_frequencies), 2)]
    decoded_text = ""
    for pair in pairs:
        nibble_1 = pair[0]
        nibble_2 = pair[1]
        relevant_row = excel_data[(excel_data['nibble 1 (Hz)'] == nibble_1) & (excel_data['nibble 2 (Hz)'] == nibble_2)]
        if not relevant_row.empty:
            ascii_result = relevant_row['ascii'].values[0]

            # Check if the decoded character is "nan" and replace it with a default character
            if pd.isna(ascii_result):
                decoded_text += "'"
            elif ascii_result == "space":
                decoded_text += " "
            else:
                decoded_text += str(ascii_result)
    # Imprime o texto decodificado
    #print("Texto decodificado:", decoded_text)
    return decoded_text

# Função para plottar o gráfico da demodulação
def plot_wav(filename):
    sample_rate, data = wav.read(filename)

    data_hilbert = signal.hilbert(data)
    amplitude_envelop = np.abs(data_hilbert)
    time = np.arange(len(data)) / sample_rate

    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(time, data, label='Sinal Analítico')
    plt.plot(time, amplitude_envelop, label='Envoltória de Amplitudes')
    plt.xlabel('Tempo (s)')
    plt.legend()

    plt.subplot(2, 1, 2)
    phase_break = (np.diff(np.unwrap(np.angle(data_hilbert))) / (2.0 * np.pi) * sample_rate)
    plt.plot(time[:-1], phase_break)
    plt.xlabel('Tempo (s)')
    plt.ylim(0, 4000)

    plt.tight_layout()
    plt.show()

