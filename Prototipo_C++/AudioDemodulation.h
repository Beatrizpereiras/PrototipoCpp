#ifndef AUDIO_DEMODULATION_H
#define AUDIO_DEMODULATION_H

#include <string>

namespace AudioDemodulation {

constexpr double M_PI = 3.14159265358979323846;

std::string demodulateWav(const std::string& filename);

} // namespace AudioDemodulation

#endif // AUDIO_DEMODULATION_H
