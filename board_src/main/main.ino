#include <SoftwareSerial.h>

#define bpm_samp_siz 4
#define bpm_rise_threshold 4

int bpm_pin = 0;

SoftwareSerial bpm_serial(6,5); // RX, TX

void setup() {
  Serial.begin(115200);
  Serial.println("Arduino started");

  bpm_serial.begin(9600);
}

void loop ()
{
  /* SETUP */
  
  /* BPM Sensor variables ----------------*/
  float bpm_reads[bpm_samp_siz], sum;
  long int now, ptr;
  float last_bpm, bpm_read, start;
  float before_bpm, cur_avg_bpm;
  float bpm_readings[3] = {0.0, 0.0, 0.0};
  bool rising;
  int rise_count;
  int bpm_n;
  long int last_beat;


  /* BPM readings init ---------------- */
  for (int i = 0; i < bpm_samp_siz; i++)
    bpm_reads[i] = 0;
  sum = 0;
  ptr = 0;


  /* MAIN LOOP  ---------------- */
  while(1)
  {
    

    
    /* BPM readings start ---------------- */
    bpm_n = 0;
    start = millis();
    bpm_read = 0.;
    do
    {
      bpm_read += analogRead(bpm_pin);
      bpm_n++;
      now = millis();
    }
    while (now < start +  20);  
    bpm_read /= bpm_n;
    
    sum -= bpm_reads[ptr];
    sum += bpm_read;
    bpm_reads[ptr] = bpm_read;
    last_bpm = sum / bpm_samp_siz;      // average of the bpm readings

    // check for a rising curve (= a heart beat)
    if (last_bpm > before_bpm)
    {
      rise_count++;
      if (!rising && rise_count > bpm_rise_threshold)
      {
        // The rising flag prevents us from detecting the same rise more than once.
        rising  = true;
        bpm_readings[0] = millis() - last_beat;
        last_beat = millis();

        // Calculate the weighed average of heartbeat rate
        // according  to the three last beats
        cur_avg_bpm = 60000. / (0.4 * bpm_readings[0] + 0.3 * bpm_readings[1] + 0.3 * bpm_readings[2]);
        
        // sending data to the node mcu
        bpm_serial.println(cur_avg_bpm, 2);

        // Serial.print(cur_avg_bpm);
        // Serial.print('\n');
        
        bpm_readings[2] = bpm_readings[1];
        bpm_readings[1] = bpm_readings[0];
      }
    }
    else
    {
      rising = false;
      rise_count = 0;
    }
    before_bpm = last_bpm;
    
    
    ptr++;
    ptr %= bpm_samp_siz;
  }
}

 
