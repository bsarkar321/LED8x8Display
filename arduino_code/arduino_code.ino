// FFT library options
// See http://wiki.openmusiclabs.com/wiki/Defines if you're curious.
#define FFT_N 16 // you can change this if you like - see the note in setLEDs.
                 // (you might consider changing it to 64)
#define WINDOW 0
#define OCTAVE 1
#define OCT_NORM 0

#define BUF_LEN 33

#include <FFT.h>

const byte ANODE_PINS[8] = {6, 7, 8, 9, 10, 11, 12, 13};
const byte CATHODE_PINS[8] = {2, 3, 4, 5, A0, A1, A2, A3};

const byte SAMPLE_PERIOD_MICROSECONDS = 250;
const byte AUDIO_INPUT_PIN = A5;

void setup() {
  Serial.begin(115200);

  pinMode(AUDIO_INPUT_PIN, INPUT);
  for (byte i = 0; i < 8; i++) {
    pinMode(ANODE_PINS[i], OUTPUT);
    pinMode(CATHODE_PINS[i], OUTPUT);
    digitalWrite(ANODE_PINS[i], HIGH);
    digitalWrite(CATHODE_PINS[i], HIGH);
  }
}

/* Function: display
 * -----------------
 * Runs through one multiplexing cycle of the LEDs, controlling which LEDs are
 * on.
 *
 * During this function, LEDs that should be on will be turned on momentarily,
 * one row at a time. When this function returns, all the LEDs will be off
 * again, so it needs to be called continuously for LEDs to be on.
 */
void display(byte pattern[8][8]) {
  for (byte bright = 0; bright < 15; bright++) {
    for (byte row = 0; row < 8; row++) {
      for (byte col = 0; col < 8; col++) {
        // Turn on (LOW) if pattern is 1, else turn off (HIGH)
        digitalWrite(CATHODE_PINS[col], pattern[row][col] > bright ? LOW : HIGH);
      }
      digitalWrite(ANODE_PINS[row], LOW);
      delayMicroseconds(2 * bright + 1);
      digitalWrite(ANODE_PINS[row], HIGH);
    }
  }
}

/* Function: getSamples
 * --------------------
 * Populates every other element of an array with FFT_N samples, sampled at
 * 1000/SAMPLE_PERIOD_MICROSECONDS kHz. Takes about 6.7ms to run.
 */
void getSamples(int samples[FFT_N*2]) {
  unsigned long next_sample_time = micros();
  for (byte i = 0; i < FFT_N*2; i+=2) {
    while (micros() < next_sample_time); // wait till next sample time
    unsigned long value = analogRead(AUDIO_INPUT_PIN);
    samples[i] = value - 512;   // TO DO: Change 512 to be average value of biasing circuit  
    samples[i+1] = 0;
    next_sample_time += SAMPLE_PERIOD_MICROSECONDS;
  }
}

void printBins(byte bins[LOG_N]) {
  static char message[20];
  sprintf(message, "%3d %3d %3d %3d\n", fft_oct_out[0], fft_oct_out[1], fft_oct_out[2], fft_oct_out[3]);
  Serial.print(message);
}

void loop() {
  static byte ledOn[8][8] = {
    {1, 1, 1, 1, 1, 1, 1, 1},
    {1, 1, 1, 1, 1, 1, 1, 1},
    {1, 1, 1, 1, 1, 1, 1, 1},
    {1, 1, 1, 1, 1, 1, 1, 1},
    {1, 1, 1, 1, 1, 1, 1, 1},
    {1, 1, 1, 1, 1, 1, 1, 1},
    {1, 1, 1, 1, 1, 1, 1, 1},
    {1, 1, 1, 1, 1, 1, 1, 1}    
  };
  static byte pattern[8][8];
  static byte use_audio = 0;
  static byte buffer[33];
  static byte offset = 0;

  if (Serial.available() > 0 && offset < BUF_LEN) {
    offset += Serial.readBytes(buffer + offset, BUF_LEN - offset);
    if (offset == BUF_LEN) {
      for (int i = 0; i < 8; i++) {
        for (int j = 0; j < 4; j++) {
          byte buf = buffer[4 * i + j];
          ledOn[i][2 * j] = (buf & 0xF);
          ledOn[i][2 * j+1] = ((buf >> 4) & 0xF);
        }
      }
      use_audio = buffer[BUF_LEN - 1];
      offset = 0;
    }
  } else if (use_audio) {
    getSamples(fft_input);
    fft_reorder();
    fft_run();
    fft_mag_octave();

    // printBins(fft_oct_out);
    for (int j = 0; j < 8; j++) {
      byte fft_bin = fft_oct_out[j / 2] / 12;
      for (int i = 0; i < 8; i++) {
        pattern[i][j] = (ledOn[i][j] > 0) * (i > fft_bin ? 15 : 4);

      }
    }
  } else {
    for (int i = 0; i < 8; i++) {
      for (int j = 0; j < 8; j++) {
        pattern[i][j] = ledOn[i][j];

      }
    }
  }


  // This function gets called every loop
  display(pattern);
}
