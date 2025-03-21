#ifndef AUDIO_MODULATION_H
#define AUDIO_MODULATION_H

#include <vector>
#include <string>

namespace AudioModulation {

const int SAMPLE_RATE = 48000;
constexpr double M_PI = 3.14159265358979323846;

std::vector<float> generateTone(int bitNumber, double durationSeconds, double minFreq, double maxFreq);
std::vector<float> generateIncreasingTone(double durationSeconds, double minFreq, double maxFreq);
std::vector<float> generateDecreasingTone(double durationSeconds, double minFreq, double maxFreq);
std::vector<float> textToTone(const std::string& text, double durationSeconds, double minFreq, double maxFreq);
bool writeWav(const std::string& filename, const std::vector<float>& samples);

} // namespace AudioModulation

#endif // AUDIO_MODULATION_H
