import os
import random
import string

import numpy as np
from scipy.io import wavfile

from css_mod import generate_increasing_tone, generate_tone, generate_decreasing_tone
from css_demod import demodule_wav


def generate_wav(text, filename, duration_seconds=1.0):
    output_folder = "wav_files"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_filename = os.path.join(output_folder, filename + ".wav")
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




# Função para gerar texto aleatório
def generate_random_text(length):
    return ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation + ' ') for _ in range(length))

# Função para calcular a porcentagem de acertos
def calculate_accuracy(original_text, decoded_text):
    correct_count = sum(1 for o, d in zip(original_text, decoded_text) if o == d)
    total_chars = len(original_text)
    accuracy_percentage = (correct_count / total_chars) * 100
    return accuracy_percentage

# Função para executar o processo de modulação, demodulação e comparação
def test_modulation_demodulation_in_mass(iterations, text_length=100, duration_seconds=1.0):
    successful_tests = 0
    total_accuracy = 0
    failed_tests = []

    for _ in range(iterations):
        original_text = generate_random_text(text_length)

        # Modulation and demodulation
        folder = "wav_files"
        filename = "original.wav"
        generate_wav(original_text, filename, duration_seconds)
        file_path = os.path.join(folder, filename + ".wav")
        decoded_text = demodule_wav(file_path)

        # Comparison and accuracy calculation
        accuracy_percentage = calculate_accuracy(original_text, decoded_text)

        if accuracy_percentage == 100.0:
            successful_tests += 1

            print(f"Original Text:  {original_text}")
            print(f"Decoded Text:   {decoded_text}")
        else:
            failed_tests.append({
                "original_text": original_text,
                "decoded_text": decoded_text,
                "accuracy": accuracy_percentage
            })

        total_accuracy += accuracy_percentage
        print(_)

    average_accuracy = total_accuracy / iterations
    success_rate = (successful_tests / iterations) * 100

    print(f"\nTest Results for {iterations} Iterations:")
    print(f"Average Accuracy: {average_accuracy:.2f}%")
    print(f"Success Rate: {success_rate:.2f}%")

    if failed_tests:
        print("\nFailed Tests:")
        for i, failed_test in enumerate(failed_tests, start=1):
            print(f"\nFailed Test {i}:")
            print(f"Original Text: {failed_test['original_text']}")
            print(f"Decoded Text: {failed_test['decoded_text']}")
            print(f"Accuracy: {failed_test['accuracy']:.2f}%")

# Example usage with 1000 iterations
test_modulation_demodulation_in_mass(10)


