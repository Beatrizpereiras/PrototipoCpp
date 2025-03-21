#include "AudioModulation.h"
#include "AudioDemodulation.h"
#include <iostream>
#include <string>

int main() {
    std::cout << "Programa Modulador/Demodulador\n";
    std::cout << "1. Modula Texto para WAV\n";
    std::cout << "2. Demodula WAV para Texto\n";
    std::cout << "Escolha uma opção: ";
    int choice;
    std::cin >> choice;
    std::cin.ignore(); // limpar newline

    const double defaultDuration = 1.0;
    const double defaultMinFreq = 1000;
    const double defaultMaxFreq = 2000;

    if (choice == 1) {
        std::string text;
        std::cout << "Digite o texto a ser modulado: ";
        std::getline(std::cin, text);
        auto samples = AudioModulation::textToTone(text, defaultDuration, defaultMinFreq, defaultMaxFreq);
        std::string filename;
        std::cout << "Digite o nome do arquivo WAV de saída: ";
        std::getline(std::cin, filename);
        if (AudioModulation::writeWav(filename.append(".wav"), samples)) {
            std::cout << "Arquivo WAV salvo com sucesso.\n";
        } else {
            std::cout << "Erro ao salvar o arquivo WAV.\n";
        }
    } else if (choice == 2) {
        std::string filename;
        std::cout << "Digite o nome do arquivo WAV para demodulação: ";
        std::getline(std::cin, filename);
        std::string demodText = AudioDemodulation::demodulateWav(filename);
        std::cout << "Texto demodulado: " << demodText << "\n";
    } else {
        std::cout << "Opção inválida.\n";
    }

    return 0;
}
