#include "AudioModulation.h"
#include <cmath>
#include <fstream>
#include <iostream>
#include <cstdint>
#include <vector>
#include <cstring>

namespace AudioModulation {

static void appendSamples(std::vector<float>& dest, const std::vector<float>& src) {
    dest.insert(dest.end(), src.begin(), src.end());
}

std::vector<float> generateTone(int bitNumber, double durationSeconds, double minFreq, double maxFreq) {
    int totalSamples = static_cast<int>(SAMPLE_RATE * durationSeconds);
    std::vector<float> samples(totalSamples);
    double range = maxFreq - minFreq;
    double baseFreq = minFreq + (static_cast<double>(bitNumber) / 16.0) * range;
    for (int i = 0; i < totalSamples; i++) {
        double t = static_cast<double>(i) / SAMPLE_RATE;
        double freq = baseFreq + (range * t / durationSeconds);
        while (freq > maxFreq) {
            freq -= range;
        }
        samples[i] = static_cast<float>(std::sin(2 * M_PI * freq * t));
    }
    return samples;
}

std::vector<float> generateIncreasingTone(double durationSeconds, double minFreq, double maxFreq) {
    int totalSamples = static_cast<int>(SAMPLE_RATE * durationSeconds / 2);
    std::vector<float> samples(totalSamples);
    double startFreq = minFreq, endFreq = maxFreq;
    for (int i = 0; i < totalSamples; i++) {
        double t = static_cast<double>(i) / SAMPLE_RATE;
        double freq = startFreq + (endFreq - startFreq) * (static_cast<double>(i) / totalSamples);
        samples[i] = static_cast<float>(std::sin(2 * M_PI * freq * t));
    }
    return samples;
}

std::vector<float> generateDecreasingTone(double durationSeconds, double minFreq, double maxFreq) {
    int totalSamples = static_cast<int>(SAMPLE_RATE * durationSeconds / 2);
    std::vector<float> samples(totalSamples);
    double startFreq = maxFreq, endFreq = minFreq;
    for (int i = 0; i < totalSamples; i++) {
        double t = static_cast<double>(i) / SAMPLE_RATE;
        double freq = startFreq + (endFreq - startFreq) * (static_cast<double>(i) / totalSamples);
        samples[i] = static_cast<float>(std::sin(2 * M_PI * freq * t));
    }
    return samples;
}

std::vector<float> textToTone(const std::string& text, double durationSeconds, double minFreq, double maxFreq) {
    std::vector<float> tones;
    // Sync chirps: três tons crescentes concatenados
    auto sync = generateIncreasingTone(durationSeconds, minFreq, maxFreq);
    std::vector<float> syncTrip;
    syncTrip.insert(syncTrip.end(), sync.begin(), sync.end());
    syncTrip.insert(syncTrip.end(), sync.begin(), sync.end());
    syncTrip.insert(syncTrip.end(), sync.begin(), sync.end());
    appendSamples(tones, syncTrip);
    
    // Para cada caractere gera dois tons (nibbles)
    for (char c : text) {
        int value = static_cast<int>(c);
        int firstHalf = (value >> 4) & 0xF;
        int secondHalf = value & 0xF;
        auto tone1 = generateTone(firstHalf, durationSeconds / 2, minFreq, maxFreq);
        auto tone2 = generateTone(secondHalf, durationSeconds / 2, minFreq, maxFreq);
        appendSamples(tones, tone1);
        appendSamples(tones, tone2);
    }
    
    // End chirps: dois tons decrescentes concatenados
    auto endTone = generateDecreasingTone(durationSeconds, minFreq, maxFreq);
    appendSamples(tones, endTone);
    appendSamples(tones, endTone);
    
    return tones;
}

// Escrita simples de arquivo WAV (PCM 16-bit)
bool writeWav(const std::string& filename, const std::vector<float>& samples) {
    int numSamples = static_cast<int>(samples.size());
    int sampleRate = SAMPLE_RATE;
    int bitsPerSample = 16;
    int numChannels = 1;
    int byteRate = sampleRate * numChannels * bitsPerSample / 8;
    int blockAlign = numChannels * bitsPerSample / 8;
    int subchunk2Size = numSamples * numChannels * bitsPerSample / 8;
    int chunkSize = 4 + (8 + 16) + (8 + subchunk2Size);
    
    std::ofstream out(filename, std::ios::binary);
    if (!out) {
        std::cerr << "Não foi possível abrir o arquivo para escrita: " << filename << "\n";
        return false;
    }
    
    // RIFF header
    out.write("RIFF", 4);
    out.write(reinterpret_cast<const char*>(&chunkSize), 4);
    out.write("WAVE", 4);
    
    // fmt subchunk
    out.write("fmt ", 4);
    int subchunk1Size = 16;
    out.write(reinterpret_cast<const char*>(&subchunk1Size), 4);
    short audioFormat = 1;
    out.write(reinterpret_cast<const char*>(&audioFormat), 2);
    out.write(reinterpret_cast<const char*>(&numChannels), 2);
    out.write(reinterpret_cast<const char*>(&sampleRate), 4);
    out.write(reinterpret_cast<const char*>(&byteRate), 4);
    out.write(reinterpret_cast<const char*>(&blockAlign), 2);
    out.write(reinterpret_cast<const char*>(&bitsPerSample), 2);
    
    // data subchunk
    out.write("data", 4);
    out.write(reinterpret_cast<const char*>(&subchunk2Size), 4);
    
    // Escrever amostras em 16-bit
    for (float sample : samples) {
        if (sample > 1.0f) sample = 1.0f;
        if (sample < -1.0f) sample = -1.0f;
        int16_t intSample = static_cast<int16_t>(sample * 32767);
        out.write(reinterpret_cast<const char*>(&intSample), sizeof(int16_t));
    }
    out.close();
    return true;
}

} // namespace AudioModulation
